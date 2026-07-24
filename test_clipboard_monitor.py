#!/usr/bin/env python3
"""
Standalone test for hybrid clipboard monitoring.

How to test:
1. Run: ./.venv/bin/python3 test_clipboard_monitor.py
2. Copy things normally (Ctrl+C, right-click Copy, select text, etc.)
3. Watch the terminal — it prints every capture in real time
4. Press Ctrl+C IN THE TERMINAL to stop the test
5. Check the JSON file at ~/.cache/multiclip/test_history.json

What it tests:
- pynput detecting Ctrl+C globally
- Clipboard read after 100ms delay
- Fallback polling every 1 second
- Deduplication (won't save same text twice)
- JSON persistence
"""

import os
import sys
import time
import json
import threading
from datetime import datetime
from pynput import keyboard as pkb

# Try to import pyperclip
try:
    import pyperclip
except ImportError:
    print("ERROR: pyperclip not installed. Run: pip install pyperclip")
    sys.exit(1)

# Config
POLL_INTERVAL = 1.0      # seconds (fallback poll)
CTRL_C_DELAY = 0.10      # seconds (wait for clipboard after Ctrl+C)
TEST_DURATION = 60       # seconds (auto-stop, or Ctrl+C to stop early)
SAVE_PATH = os.path.expanduser("~/.cache/multiclip/test_history.json")

os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)

class ClipboardMonitorTest:
    def __init__(self):
        self.history = []
        self.last_clipboard = ""
        self.lock = threading.Lock()
        self.running = True
        self.start_time = time.time()
        self.ctrl_c_count = 0
        self.poll_count = 0
        self.listener = None
        self.held_keys = set()

    def _save(self):
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def _capture(self, source):
        """Read clipboard and save if changed."""
        try:
            text = pyperclip.paste()
        except Exception as e:
            print(f"  [ERROR reading clipboard: {e}]")
            return

        if not text or text == self.last_clipboard:
            return

        self.last_clipboard = text
        entry = {
            "id": len(self.history) + 1,
            "time": datetime.now().isoformat(),
            "source": source,
            "preview": text[:80].replace("\n", " "),
            "length": len(text)
        }

        with self.lock:
            self.history.append(entry)
            self._save()

        preview = text[:60].replace("\n", " ")
        if len(text) > 60:
            preview += "..."
        print(f"  [{source}] #{entry['id']} ({len(text)} chars): {preview}")

    def _on_ctrl_c_detected(self):
        """Called when Ctrl+C is pressed."""
        self.ctrl_c_count += 1
        # Wait a bit for the application to put data on the clipboard
        def delayed_capture():
            time.sleep(CTRL_C_DELAY)
            if self.running:
                self._capture("ctrl+c")
        threading.Thread(target=delayed_capture, daemon=True).start()

    def _poll_loop(self):
        """Fallback polling thread."""
        while self.running:
            time.sleep(POLL_INTERVAL)
            if not self.running:
                break
            self.poll_count += 1
            self._capture("poll")

    def _on_key_press(self, key):
        try:
            k = str(key).lower()
            if 'ctrl' in k:
                self.held_keys.add('ctrl')
            if hasattr(key, 'char') and key.char and key.char.lower() == 'c' and 'ctrl' in self.held_keys:
                self._on_ctrl_c_detected()
        except Exception:
            pass

    def _on_key_release(self, key):
        try:
            k = str(key).lower()
            if 'ctrl' in k:
                self.held_keys.discard('ctrl')
        except Exception:
            pass

    def run(self):
        print("=" * 60)
        print("CLIPBOARD MONITOR TEST")
        print("=" * 60)
        print(f"Save path: {SAVE_PATH}")
        print(f"Poll interval: {POLL_INTERVAL}s")
        print(f"Ctrl+C delay: {CTRL_C_DELAY}s")
        print(f"Auto-stop after: {TEST_DURATION}s")
        print("")
        print("INSTRUCTIONS:")
        print("  1. Switch to another window (browser, terminal, etc.)")
        print("  2. Copy text however you want:")
        print("     - Ctrl+C")
        print("     - Right-click > Copy")
        print("     - Select text with mouse")
        print("  3. Watch this terminal — captures appear in real time")
        print("  4. Press Ctrl+C IN THIS TERMINAL to stop early")
        print("")
        print("Starting in 3 seconds...")
        time.sleep(3)
        print("LISTENING. Go copy some things!\n")

        # Start keyboard listener
        self.listener = pkb.Listener(on_press=self._on_key_press, on_release=self._on_key_release)
        self.listener.start()

        # Start poll thread
        poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        poll_thread.start()

        # Run until stopped or timeout
        try:
            while self.running:
                time.sleep(0.1)
                elapsed = time.time() - self.start_time
                if elapsed >= TEST_DURATION:
                    print(f"\n[INFO] Auto-stopped after {TEST_DURATION} seconds.")
                    break
        except KeyboardInterrupt:
            print("\n[INFO] Stopped by user (Ctrl+C).")
        finally:
            self.running = False
            if self.listener:
                self.listener.stop()

        # Summary
        elapsed = time.time() - self.start_time
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Runtime:        {elapsed:.1f}s")
        print(f"Total captures: {len(self.history)}")
        print(f"Ctrl+C detects: {self.ctrl_c_count}")
        print(f"Poll checks:    {self.poll_count}")
        print(f"Saved to:       {SAVE_PATH}")
        print("")
        if self.history:
            print("Last 5 captures:")
            for e in self.history[-5:]:
                print(f"  #{e['id']} [{e['source']}] {e['preview'][:50]}...")
        print("")
        print("If you copied 10 things and see 10 captures, the test passed.")
        print("If numbers don't match, we missed something and need to tune.")


if __name__ == "__main__":
    test = ClipboardMonitorTest()
    test.run()
