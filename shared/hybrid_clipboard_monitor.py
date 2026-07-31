"""
Hybrid Clipboard Monitor — replaces ClipmanParser with live clipboard capture.

Proven approach from test_clipboard_monitor.py:
- pynput detects Ctrl+C globally → waits 100ms → reads pyperclip
- Fallback poll every 1s catches right-click/menu copies
- Deduplication (won't save same text twice)
- JSON persistence to ~/.cache/multiclip/clipboard_history.json

Implements the same interface as ClipmanParser for drop-in replacement:
- filepath attribute (for mtime polling compatibility)
- parse(max_entries) -> List[MonitorEntry]
- get_recent(count) -> List[MonitorEntry]
"""

import os
import time
import json
import threading
from typing import List, Optional

from pynput import keyboard as pkb


try:
    import pyperclip
except ImportError:
    pyperclip = None


class MonitorEntry:
    """Entry object compatible with ClipEntry interface."""
    def __init__(self, data: dict):
        self.id = data.get("id", 0)
        self.decoded_content = data.get("content", "")
        self.preview = data.get("preview", "")[:80]
        self.word_count = len(self.decoded_content.split())
        self.time = data.get("time", 0)  # unix timestamp, 0 if unknown

    @property
    def is_empty(self) -> bool:
        return not self.decoded_content.strip()


class HybridClipboardMonitor:
    """
    Drop-in replacement for ClipmanParser that captures clipboard live.
    """

    POLL_INTERVAL = 1.0      # seconds (fallback poll)
    CTRL_C_DELAY = 0.10      # seconds (wait for clipboard after Ctrl+C)
    MAX_HISTORY = 100000

    def __init__(self, save_path: Optional[str] = None):
        self.save_path = save_path or os.path.expanduser(
            "~/.cache/multiclip/clipboard_history.json"
        )
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        self.filepath = self.save_path  # For compatibility with mtime polling

        self.history: List[dict] = []
        self.last_clipboard = ""
        self.lock = threading.Lock()
        self.running = True
        self.ctrl_c_count = 0
        self.poll_count = 0
        self.listener: Optional[pkb.Listener] = None
        self.held_keys: set = set()

        self._load_history()
        self._start_monitoring()

    # ---------------- Persistence ----------------
    def _load_history(self):
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                    if not isinstance(self.history, list):
                        self.history = []
            except Exception:
                self.history = []

    def _save(self):
        try:
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[HybridClipboardMonitor] save error: {e}")

    # ---------------- Capture ----------------
    def _capture(self, source: str):
        """Read clipboard and save if changed."""
        if pyperclip is None:
            return

        try:
            text = pyperclip.paste()
        except Exception as e:
            print(f"  [HybridClipboardMonitor] clipboard read error: {e}")
            return

        if not text or text == self.last_clipboard:
            return

        self.last_clipboard = text
        entry = {
            "id": len(self.history) + 1,
            "time": time.time(),
            "source": source,
            "content": text,
            "preview": text[:80].replace("\n", " "),
            "length": len(text),
        }

        with self.lock:
            self.history.insert(0, entry)  # newest first
            # Keep last MAX_HISTORY entries
            if len(self.history) > self.MAX_HISTORY:
                self.history = self.history[: self.MAX_HISTORY]
            self._save()

        preview = text[:60].replace("\n", " ")
        if len(text) > 60:
            preview += "..."
        print(
            f"  [HybridClipboardMonitor] [{source}] #{entry['id']} "
            f"({len(text)} chars): {preview}"
        )

    def _on_ctrl_c_detected(self):
        """Called when Ctrl+C is pressed."""
        self.ctrl_c_count += 1

        def delayed_capture():
            time.sleep(self.CTRL_C_DELAY)
            if self.running:
                self._capture("ctrl+c")

        threading.Thread(target=delayed_capture, daemon=True).start()

    def _poll_loop(self):
        """Fallback polling thread."""
        while self.running:
            time.sleep(self.POLL_INTERVAL)
            if not self.running:
                break
            self.poll_count += 1
            self._capture("poll")

    # ---------------- Keyboard Listener ----------------
    def _on_key_press(self, key):
        try:
            k = str(key).lower()
            if "ctrl" in k:
                self.held_keys.add("ctrl")
            if (
                hasattr(key, "char")
                and key.char
                and key.char.lower() == "c"
                and "ctrl" in self.held_keys
            ):
                self._on_ctrl_c_detected()
        except Exception:
            pass

    def _on_key_release(self, key):
        try:
            k = str(key).lower()
            if "ctrl" in k:
                self.held_keys.discard("ctrl")
        except Exception:
            pass

    def _start_monitoring(self):
        self.listener = pkb.Listener(
            on_press=self._on_key_press, on_release=self._on_key_release
        )
        self.listener.start()
        poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        poll_thread.start()
        print(
            "[HybridClipboardMonitor] Started: "
            f"poll={self.POLL_INTERVAL}s, ctrl_c_delay={self.CTRL_C_DELAY}s"
        )

    def stop(self):
        """Stop monitoring threads. Call before exit."""
        self.running = False
        if self.listener:
            self.listener.stop()
        print("[HybridClipboardMonitor] Stopped.")

    # ---------------- ClipmanParser-compatible API ----------------
    def parse(self, max_entries: int = 200, offset: int = 0) -> List[MonitorEntry]:
        """Return most recent entries first (newest = index 0).
        Supports pagination with offset for on-demand loading."""
        with self.lock:
            start = offset
            end = offset + max_entries
            recent = self.history[start:end]
        return [MonitorEntry(e) for e in recent if e.get("content", "").strip()]

    def get_total_count(self) -> int:
        """Return total number of history entries."""
        with self.lock:
            return len(self.history)

    def get_recent(self, count: int = 50) -> List[MonitorEntry]:
        return self.parse(max_entries=count)


# Quick standalone test helper
if __name__ == "__main__":
    monitor = HybridClipboardMonitor()
    print("Monitor running. Copy some text. Press Ctrl+C in terminal to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
        print(f"\nCaptured {len(monitor.history)} entries total.")
        for e in monitor.get_recent(5):
            print(f"  [{e.id}] {e.preview[:50]}...")
