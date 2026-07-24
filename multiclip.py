#!/usr/bin/env python3
"""
MultiClip V2 — Current Working Version
Now temporarily loading the old GUI from gui/main_window.py for review.
"""

import pyperclip
import pyautogui
import subprocess
import time
import json
import os
import sys
import fcntl
import threading
import hashlib
import tkinter as tk
from pynput import keyboard as pkb

from shared.hybrid_clipboard_monitor import HybridClipboardMonitor

# Try to load the old dense UI the user likes
try:
    from gui.main_window import MainWindow
    USE_OLD_UI = True
except Exception as e:
    print(f"Could not load old GUI: {e}")
    USE_OLD_UI = False


class MultiClipV2:
    def __init__(self):
        # --- Single-instance guard (kernel-level flock) ---
        self._lock_file = None
        self._ensure_single_instance()

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.dict_file = os.path.join(self.base_dir, "clipboard_dict.json")
        self.icon_path = os.path.join(self.base_dir, "chargers.png")

        self.slots = {str(i): "" for i in range(1, 31)}
        self.load_slots()

        self.listener = None
        self.held_mods = set()

        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.02

        # Orderly mode state
        self.orderly_active = False
        self.orderly_submode = "fifo"       # "fifo" | "lifo"
        self.orderly_copy_cursor = 1        # next empty slot to fill (1-30)
        self.orderly_paste_cursor = 1       # next filled slot to paste (1-30)
        self.orderly_wrap_count = 0
        self.orderly_last_clip_hash = ""
        self.orderly_last_capture_time = 0
        self.orderly_timer = None

        # Make sure we persist slot state even on abrupt kill (Ctrl+C etc.)
        import signal, atexit
        def _emergency_save():
            try:
                self.save_slots()
            except:
                pass
            try:
                if hasattr(self, 'clipboard_monitor') and self.clipboard_monitor:
                    self.clipboard_monitor.stop()
            except:
                pass
            try:
                self._stop_orderly_timer()
            except:
                pass
        atexit.register(_emergency_save)
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, lambda s, f: (_emergency_save(), sys.exit(0)))
            except:
                pass

        # Start hotkeys first (listener runs in background thread)
        self._register_hotkeys()

        if USE_OLD_UI:
            print("Loading old dense UI from gui/main_window.py ...")
            self.ui = MainWindow()
            self._wire_old_ui()
            self._wire_clipman_panel()
            # This will block on mainloop
            self.ui.run()
        else:
            print("Falling back to simple UI")
            self._build_simple_ui()
            self.root.mainloop()

    # ---------------- Persistence ----------------
    def load_slots(self):
        if not os.path.exists(self.dict_file):
            self.save_slots()
            return
        try:
            with open(self.dict_file, "r") as f:
                data = json.load(f)
            if isinstance(data, dict) and "slots" in data:
                for k, v in data["slots"].items():
                    sid = str(k) if k.isdigit() else k.replace("slot_", "")
                    if sid in self.slots:
                        self.slots[sid] = v.get("content", "") if isinstance(v, dict) else str(v)
            else:
                for k, v in data.items():
                    if str(k).startswith("slot_"):
                        sid = str(k).split("_", 1)[1]
                        if sid in self.slots:
                            self.slots[sid] = str(v) if v else ""
                    elif str(k) in self.slots:
                        self.slots[str(k)] = str(v) if v else ""
        except Exception as e:
            print(f"[LOAD] {e}")

    def save_slots(self):
        with open(self.dict_file, "w") as f:
            json.dump({"slots": {str(i): self.slots[str(i)] for i in range(1, 31)}}, f, indent=2)

    # ---------------- Old UI Wiring ----------------
    def _wire_old_ui(self):
        """Minimal wiring so the old UI can launch and display slots."""
        try:
            # Populate the old UI with current slots
            for i in range(1, 31):
                content = self.slots.get(str(i), "")
                preview = content[:60] + "..." if len(content) > 60 else content
                if hasattr(self.ui, "update_slot"):
                    self.ui.update_slot(i-1, content, preview)
                elif hasattr(self.ui, "slot_displays"):
                    if i-1 in self.ui.slot_displays:
                        self.ui.slot_displays[i-1].update_content(content, preview)

            # Wire new callbacks
            if hasattr(self.ui, "set_preview_transfer_callback"):
                self.ui.set_preview_transfer_callback(self._transfer_single_to_slot)
            if hasattr(self.ui, "set_one_per_line_callback"):
                self.ui.set_one_per_line_callback(self._transfer_clipman_one_per_line)
            if hasattr(self.ui, "set_send_to_snippet_callback"):
                self.ui.set_send_to_snippet_callback(self._send_to_snippets)
            if hasattr(self.ui, "set_orderly_submode_callback"):
                self.ui.set_orderly_submode_callback(self._set_orderly_submode)
            if hasattr(self.ui, "set_slot_click_callback"):
                self.ui.set_slot_click_callback(self._on_manual_slot_clicked)
            if hasattr(self.ui, "set_orderly_paste_callback"):
                self.ui.set_orderly_paste_callback(self.orderly_paste_next)
            if hasattr(self.ui, "set_copy_to_clipboard_callback"):
                self.ui.set_copy_to_clipboard_callback(self._copy_to_clipboard)
            if hasattr(self.ui, "mode_change_callback"):
                self.ui.mode_change_callback = self._on_mode_change

            # Start external command polling (for XFCE hotkeys, etc.)
            self._start_cmd_polling()

        except Exception as e:
            print(f"Error wiring old UI: {e}")
            import traceback
            traceback.print_exc()
            print("Falling back to simple UI...")
            self._build_simple_ui()

    def _on_manual_slot_clicked(self, slot_id: int):
        """When user clicks a slot in manual mode, record it."""
        if hasattr(self.ui, "manual_start_slot"):
            self.ui.manual_start_slot = slot_id + 1  # convert 0-based to 1-based

    def _set_orderly_submode(self, mode: str):
        self.orderly_submode = mode

    def _on_mode_change(self, mode: str):
        if mode == "Orderly":
            self.start_orderly_monitor()
        else:
            self.stop_orderly_monitor()

    def _copy_to_clipboard(self, content: str, source: str):
        """Copy selected content to the system clipboard for regular Ctrl+V pasting."""
        try:
            pyperclip.copy(content)
            self.show_toast("COPIED", f"{source} → clipboard ({len(content)} chars)")
        except Exception as e:
            self.show_toast("COPY FAILED", str(e))

    def _ensure_single_instance(self):
        """Prevent multiple MultiClip instances using an exclusive flock.
        Lock is placed in /tmp so both root and flintx can see it.
        """
        lock_path = "/tmp/multiclip.lock"
        self._lock_file = open(lock_path, "w")
        try:
            fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("[MULTICLIP] Another instance is already running. Exiting.")
            sys.exit(1)

    def _wire_clipman_panel(self):
        """Wire the hybrid clipboard monitor to the Clipman History panel."""
        try:
            self.clipboard_monitor = HybridClipboardMonitor()
            entries = self.clipboard_monitor.parse(max_entries=9999)

            print(f"[CLIPMAN] Loaded {len(entries)} history entries for the right panel")

            if hasattr(self.ui, "set_clipman_entries"):
                self.ui.set_clipman_entries(entries)

            if hasattr(self.ui, "set_clipman_transfer_callback"):
                self.ui.set_clipman_transfer_callback(self._transfer_clipman_to_og_slots)

            # Start live polling so new clipboard items appear without restart
            if hasattr(self.ui, "start_live_clipman_refresh"):
                self.ui.start_live_clipman_refresh(self.clipboard_monitor, interval_ms=3000)
                print("[CLIPMAN] Live refresh polling started (every 3s)")

            if len(entries) == 0:
                print("[CLIPMAN] NOTE: No history yet. Copy some text to populate the panel.")

        except Exception as e:
            print(f"Could not wire Clipman panel: {e}")
            import traceback
            traceback.print_exc()

    def _transfer_clipman_to_og_slots(self, selected_entries, start_slot=None):
        """Smart transfer per user spec.
        - start_slot=None: fill empty slots first (batch/block bundle)
        - start_slot=N: fill sequentially from N, wrapping 30->1 (1 slot per line)
        """
        if not selected_entries:
            return []

        contents = []
        for item in selected_entries:
            if isinstance(item, str):
                contents.append(item)
            elif hasattr(item, 'decoded_content'):
                contents.append(item.decoded_content)
            else:
                contents.append(str(item))

        filled = []
        if start_slot is not None:
            # 1 slot per line mode: sequential fill from start_slot with wrap
            slot = start_slot
            for content in contents:
                self.slots[str(slot)] = content
                filled.append(slot)
                slot += 1
                if slot > 30:
                    slot = 1
        else:
            # Block bundle mode: fill empty slots first
            empty_slots = [i for i in range(1, 31) if not self.slots.get(str(i))]
            for content in contents:
                if empty_slots:
                    slot = empty_slots.pop(0)
                    self.slots[str(slot)] = content
                    filled.append(slot)
                else:
                    from tkinter import simpledialog, messagebox
                    msg = (
                        "ALL 30 OG SLOTS ARE FULL.\n\n"
                        "This item will overwrite a slot.\n"
                        "Type a slot number (1-30) to target it, or press Cancel to overwrite the oldest (slot 1)."
                    )
                    slot = simpledialog.askinteger(
                        "SLOTS FULL — Choose Target",
                        msg,
                        minvalue=1,
                        maxvalue=30,
                        initialvalue=1
                    )
                    if slot:
                        self.slots[str(slot)] = content
                        filled.append(slot)
                    else:
                        self.slots["1"] = content
                        filled.append(1)

        self.save_slots()
        self._refresh_slot_displays(filled)

        print(f"[CLIPMAN] Transferred {len(contents)} item(s) into OG slots")

        if contents:
            preview = contents[0][:70].replace("\n", " ")
            if len(contents) > 1:
                preview += f"  (+{len(contents)-1} more)"
            if start_slot is not None:
                title = f"1 per line → Slots {filled[0]:02d}-{filled[-1]:02d}"
            else:
                title = f"CLIPMAN → TRANSFER ({len(contents)} item(s))"
            self.show_toast(title, preview)
        return filled

    def _transfer_clipman_one_per_line(self, selected_entries, start_slot=1):
        """Public wrapper for 1 slot per line transfer."""
        return self._transfer_clipman_to_og_slots(selected_entries, start_slot=start_slot)

    def _transfer_single_to_slot(self, slot: int, content: str):
        """Transfer a single item directly to a specific slot (from preview popup)."""
        if 1 <= slot <= 30:
            self.slots[str(slot)] = content
            self.save_slots()
            if hasattr(self.ui, "slot_displays") and (slot-1) in self.ui.slot_displays:
                preview = content[:60] + "..." if len(content) > 60 else content
                self.ui.slot_displays[slot-1].update_content(content, preview)
            if hasattr(self.ui, "flash_slot"):
                self.ui.flash_slot(slot-1)
            self.show_toast(f"Transferred to Slot {slot:02d}", content[:70].replace("\n", " "))
            return True
        return False

    def _send_to_snippets(self, contents: list):
        """Send content(s) to the first empty snippet slot."""
        if not contents:
            return
        if not hasattr(self.ui, "snippet_entries"):
            return
        sent = 0
        for content in contents:
            for i in range(8):
                entry = self.ui.snippet_entries.get(i)
                if entry and not entry.get().strip():
                    entry.delete(0, 'end')
                    entry.insert(0, content)
                    if hasattr(self.ui, "_save_snippet"):
                        self.ui._save_snippet(i)
                    if hasattr(self.ui, "flash_snippet"):
                        self.ui.flash_snippet(i, color="#32cd32")
                    sent += 1
                    break
        if sent:
            self.show_toast(f"Saved to Snippet", f"{sent} item(s) sent to snippets")
        else:
            from tkinter import messagebox
            messagebox.showwarning("Snippets Full", "All 8 snippet slots are occupied.")

    def _refresh_slot_displays(self, slot_ids=None):
        """Refresh UI slot displays. If slot_ids is None, refresh all."""
        if not hasattr(self.ui, "slot_displays"):
            return
        if slot_ids is None:
            slot_ids = range(1, 31)
        for slot in slot_ids:
            if 1 <= slot <= 30 and (slot-1) in self.ui.slot_displays:
                c = self.slots.get(str(slot), "")
                preview = c[:60] + "..." if len(c) > 60 else c
                self.ui.slot_displays[slot-1].update_content(c, preview)

    # ---------------- Orderly Mode ----------------
    def start_orderly_monitor(self):
        self.orderly_active = True
        self._orderly_tick()
        print("[ORDERLY] Monitor started")

    def stop_orderly_monitor(self):
        self.orderly_active = False
        self._stop_orderly_timer()
        # Clear highlights
        if hasattr(self.ui, "clear_slot_highlight"):
            for i in range(30):
                self.ui.clear_slot_highlight(i)
        print("[ORDERLY] Monitor stopped")

    def _stop_orderly_timer(self):
        if self.orderly_timer:
            try:
                self.orderly_timer.cancel()
            except:
                pass
            self.orderly_timer = None

    def _orderly_tick(self):
        if not self.orderly_active:
            return
        self._orderly_clip_check()
        self.orderly_timer = threading.Timer(0.3, self._orderly_tick)
        self.orderly_timer.daemon = True
        self.orderly_timer.start()

    def _orderly_clip_check(self):
        if not self.orderly_active:
            return
        try:
            content = pyperclip.paste()
        except Exception:
            return
        if not content or not content.strip():
            return

        # Debounce: minimum 100ms between captures
        now = time.time()
        if now - self.orderly_last_capture_time < 0.1:
            return

        # Hash check for deduplication
        h = hashlib.md5(content.encode()).hexdigest()
        if h == self.orderly_last_clip_hash:
            return

        # Don't capture if it's the same as the slot we're about to write
        target_slot = str(self.orderly_copy_cursor)
        if self.slots.get(target_slot) == content:
            return

        # Suppress if GUI is focused (user typing inside MultiClip)
        if self._is_gui_focused():
            return

        self.orderly_last_clip_hash = h
        self.orderly_last_capture_time = now

        self.slots[target_slot] = content
        self.save_slots()

        # Update UI
        if hasattr(self.ui, "slot_displays") and (self.orderly_copy_cursor - 1) in self.ui.slot_displays:
            preview = content[:60] + "..." if len(content) > 60 else content
            self.ui.slot_displays[self.orderly_copy_cursor - 1].update_content(content, preview)
        if hasattr(self.ui, "flash_slot"):
            self.ui.flash_slot(self.orderly_copy_cursor - 1)

        # Advance copy cursor with wrap
        self.orderly_copy_cursor += 1
        if self.orderly_copy_cursor > 30:
            self.orderly_copy_cursor = 1
            self.orderly_wrap_count += 1

        # Update UI highlights
        if hasattr(self.ui, "clear_slot_highlight") and hasattr(self.ui, "highlight_slot"):
            for i in range(30):
                self.ui.clear_slot_highlight(i)
            self.ui.highlight_slot(self.orderly_copy_cursor - 1, color="#ff9966")

        # Update status bar
        if hasattr(self.ui, "show_orderly_status"):
            queue_len = sum(1 for i in range(1, 31) if self.slots.get(str(i)))
            self.ui.show_orderly_status(queue_len, self.orderly_paste_cursor)

        self.show_toast(f"ORDERLY COPY → Slot {target_slot}", content[:70].replace("\n", " "))

    def orderly_paste_next(self):
        """Paste from the current paste cursor and advance."""
        slot = self.orderly_paste_cursor
        content = self.slots.get(str(slot), "")
        if not content:
            self.show_toast("ORDERLY PASTE", f"Slot {slot:02d} is empty")
            return

        pyperclip.copy(content)
        time.sleep(0.12)
        self._release_all_modifiers()
        time.sleep(0.06)

        try:
            if self._is_terminal():
                subprocess.run(["xdotool", "key", "--clearmodifiers", "ctrl+shift+v"], timeout=1.0, check=False)
            else:
                subprocess.run(["xdotool", "key", "--clearmodifiers", "ctrl+v"], timeout=1.0, check=False)
        except Exception:
            if self._is_terminal():
                pyautogui.hotkey("ctrl", "shift", "v")
            else:
                pyautogui.hotkey("ctrl", "v")

        # Advance paste cursor
        if self.orderly_submode == "lifo":
            self.orderly_paste_cursor -= 1
            if self.orderly_paste_cursor < 1:
                self.orderly_paste_cursor = 30
        else:
            self.orderly_paste_cursor += 1
            if self.orderly_paste_cursor > 30:
                self.orderly_paste_cursor = 1

        # Update UI
        if hasattr(self.ui, "clear_slot_highlight") and hasattr(self.ui, "highlight_slot"):
            for i in range(30):
                self.ui.clear_slot_highlight(i)
            self.ui.highlight_slot(self.orderly_paste_cursor - 1, color="#66ff66")

        if hasattr(self.ui, "show_orderly_status"):
            queue_len = sum(1 for i in range(1, 31) if self.slots.get(str(i)))
            self.ui.show_orderly_status(queue_len, self.orderly_paste_cursor)

        self.show_toast(f"ORDERLY PASTE ← Slot {slot:02d}", content[:70].replace("\n", " "))

    def _is_gui_focused(self) -> bool:
        try:
            if hasattr(self, 'ui') and hasattr(self.ui, 'root'):
                return self.ui.root.focus_displayof() is not None
        except:
            pass
        return False

    # ---------------- External Command IPC (XFCE hotkeys, etc.) ----------------
    def _start_cmd_polling(self):
        self._cmd_file = "/tmp/multiclip.cmd"
        threading.Thread(target=self._poll_cmd_loop, daemon=True).start()

    def _poll_cmd_loop(self):
        while True:
            try:
                if os.path.exists(self._cmd_file):
                    with open(self._cmd_file, "r") as f:
                        cmd = f.read().strip()
                    if cmd:
                        os.remove(self._cmd_file)
                        if cmd == "PASTE_NEXT" and self.orderly_active:
                            if hasattr(self, 'ui') and hasattr(self.ui, 'root'):
                                self.ui.root.after(0, self.orderly_paste_next)
            except Exception as e:
                print(f"[CMD POLL] {e}")
            time.sleep(0.1)

    # ---------------- Simple fallback UI ----------------
    def _build_simple_ui(self):
        self.root = tk.Tk()
        self.root.title("MultiClip V2 (Simple Fallback)")
        self.root.geometry("860x780")
        self.root.configure(bg="#1e1e1e")
        tk.Label(self.root, text="Old GUI failed to load.\nCheck console for errors.",
                 font=("Arial", 14), bg="#1e1e1e", fg="white").pack(pady=50)
        self.root.mainloop()

    # ---------------- Defensive input & Core logic ----------------
    def _release_all_modifiers(self):
        for key in ("ctrl", "ctrl_l", "ctrl_r", "alt", "alt_l", "alt_r", "shift", "win"):
            try:
                pyautogui.keyUp(key)
            except:
                pass
        time.sleep(0.08)

    def show_toast(self, title: str, message: str):
        try:
            icon = getattr(self, "icon_path", "/home/flintx/multiclip/chargers.png")
            subprocess.run([
                "notify-send",
                "-i", icon,
                title,
                message,
                "-t", "3200"
            ], check=False)
        except Exception as e:
            print(f"[TOAST] {title} | {message}  (notify-send failed: {e})")

    def add_to_slot(self, slot_num: int):
        try:
            self._release_all_modifiers()
            pyautogui.hotkey("ctrl", "c")
            time.sleep(0.16)
            content = pyperclip.paste()
            if content and content.strip():
                self.slots[str(slot_num)] = content
                self.save_slots()
                self._refresh_slot_displays([slot_num])
                print(f"[COPY] Slot {slot_num} captured")
                preview = content[:80].replace("\n", " ")
                title = f"LEFT COMBO → COPY SLOT {slot_num:02d}"
                self.show_toast(title, preview)
            else:
                print("[COPY] Nothing captured")
        except Exception as e:
            print(f"[COPY ERROR] {e}")

    def paste_from_slot(self, slot_num: int):
        content = self.slots.get(str(slot_num), "")
        if not content:
            print(f"[PASTE] Slot {slot_num} is empty")
            return
        try:
            pyperclip.copy(content)
            time.sleep(0.12)
            self._release_all_modifiers()
            time.sleep(0.06)

            used_xdotool = False
            try:
                if self._is_terminal():
                    subprocess.run(
                        ["xdotool", "key", "--clearmodifiers", "ctrl+shift+v"],
                        timeout=1.0, check=False
                    )
                    used_xdotool = True
                else:
                    subprocess.run(
                        ["xdotool", "key", "--clearmodifiers", "ctrl+v"],
                        timeout=1.0, check=False
                    )
                    used_xdotool = True
            except Exception as xerr:
                print(f"[PASTE] xdotool failed ({xerr}), falling back to pyautogui")
                if self._is_terminal():
                    pyautogui.hotkey("ctrl", "shift", "v")
                else:
                    pyautogui.hotkey("ctrl", "v")

            method = "xdotool" if used_xdotool else "pyautogui"
            print(f"[PASTE] Slot {slot_num}  (via {method})")

            preview = content[:80].replace("\n", " ")
            title = f"RIGHT COMBO → PASTE SLOT {slot_num:02d}"
            self.show_toast(title, preview)
        except Exception as e:
            print(f"[PASTE ERROR] {e}")

    def _is_terminal(self) -> bool:
        try:
            wid = subprocess.check_output(["xdotool", "getactivewindow"], timeout=0.7).decode().strip()
            cls = subprocess.check_output(["xprop", "-id", wid, "WM_CLASS"], timeout=0.7).decode().lower()
            return any(t in cls for t in ("terminal", "xterm", "konsole", "alacritty", "kitty", "foot"))
        except:
            return False

    # ---------------- Hotkeys ----------------
    def _register_hotkeys(self):
        def on_press(key):
            try:
                k = str(key).lower()
                if 'ctrl_r' in k:
                    self.held_mods.add('ctrl_r')
                elif 'ctrl_l' in k:
                    self.held_mods.add('ctrl_l')
                elif 'ctrl' in k:
                    self.held_mods.add('ctrl')
                elif 'alt_r' in k:
                    self.held_mods.add('alt_r')
                elif 'alt_l' in k:
                    self.held_mods.add('alt_l')
                elif 'alt' in k:
                    self.held_mods.add('alt')
                else:
                    if hasattr(key, 'char') and key.char and key.char.isdigit():
                        digit = key.char
                        slot = 10 if digit == '0' else int(digit)
                        self._handle_combo(slot)
            except Exception as e:
                print(f"hotkey press err: {e}")

        def on_release(key):
            try:
                k = str(key).lower()
                if 'ctrl_r' in k:
                    self.held_mods.discard('ctrl_r')
                elif 'ctrl_l' in k:
                    self.held_mods.discard('ctrl_l')
                elif 'ctrl' in k:
                    self.held_mods.discard('ctrl')
                if 'alt_r' in k:
                    self.held_mods.discard('alt_r')
                elif 'alt_l' in k:
                    self.held_mods.discard('alt_l')
                elif 'alt' in k:
                    self.held_mods.discard('alt')
            except:
                pass

        self.listener = pkb.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()
        print("HOTKEYS: LCtrl+LAlt = copy  |  RCtrl+RAlt = paste")

    def _handle_combo(self, slot: int):
        mods = self.held_mods
        has_right = ('ctrl_r' in mods or 'alt_r' in mods)
        has_left = ('ctrl_l' in mods or 'alt_l' in mods)
        has_generic = ('ctrl' in mods and 'alt' in mods)

        if has_right and ('ctrl_r' in mods or 'ctrl' in mods) and ('alt_r' in mods or 'alt' in mods):
            print(f"[HOTKEY] Right combo → PASTE slot {slot}")
            self.paste_from_slot(slot)
        elif has_left or has_generic:
            print(f"[HOTKEY] Left combo → COPY slot {slot}")
            self.add_to_slot(slot)

    def run(self):
        if not USE_OLD_UI and hasattr(self, 'root'):
            self.root.mainloop()


if __name__ == "__main__":
    app = MultiClipV2()
    app.run()
