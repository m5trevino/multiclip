#!/usr/bin/env python3
"""
Manual hotkey test for Left-Ctrl+Alt and Right-Ctrl+Alt combos.
Run this, then hammer the combos. Watch the prints + toasts.
No full UI. Pure verification.
"""
import pyperclip
import pyautogui
import time
import subprocess
import os
from pynput import keyboard as pkb

print("=== MultiClip Hotkey Test ===")
print("Press LCtrl + LAlt + 1-0   → copy test")
print("Press RCtrl + RAlt + 1-0   → paste test")
print("Ctrl+C in this terminal to quit.\n")

def release_mods():
    for k in ("ctrl", "ctrl_l", "ctrl_r", "alt", "alt_l", "alt_r"):
        try:
            pyautogui.keyUp(k)
        except:
            pass
    time.sleep(0.06)

def test_copy(slot):
    release_mods()
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.15)
    content = pyperclip.paste()
    print(f"[COPY {slot}] captured: {content[:70]!r}")
    subprocess.run(["notify-send", "-t", "1500", "TEST COPY", f"Slot {slot}"], check=False)

def test_paste(slot):
    content = f"TEST-SLOT-{slot}-{int(time.time())}"
    pyperclip.copy(content)
    time.sleep(0.08)
    release_mods()
    pyautogui.hotkey("ctrl", "v")
    print(f"[PASTE {slot}] injected test string into active window")
    subprocess.run(["notify-send", "-t", "1500", "TEST PASTE", f"Slot {slot}"], check=False)

hotkeys = {}
for i in range(1, 11):
    k = str(i % 10)
    hotkeys[f"<ctrl_l>+<alt_l>+{k}"] = lambda s=i: test_copy(s)
    hotkeys[f"<ctrl_r>+<alt_r>+{k}"] = lambda s=i: test_paste(s)

listener = pkb.GlobalHotKeys(hotkeys)
listener.start()
print("Listener armed. Smash the combos now (LCtrl+LAlt+3, RCtrl+RAlt+7, etc).\n")
try:
    listener.join()
except KeyboardInterrupt:
    listener.stop()
    print("\nTest ended cleanly.")
