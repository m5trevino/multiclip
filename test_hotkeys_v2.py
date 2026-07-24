#!/usr/bin/env python3
"""
Improved hotkey test using RAW Listener + manual left/right tracking.
This is much more reliable than GlobalHotKeys on root + X11.

Run with the venv python:
  source .venv/bin/activate
  python test_hotkeys_v2.py

Then test:
  Left Ctrl + Left Alt + 1-0   → should COPY
  Right Ctrl + Right Alt + 1-0 → should PASTE
"""
from pynput import keyboard as pkb
import pyperclip
import pyautogui
import time
import subprocess

print("=== MultiClip Hotkey Test V2 (Raw Listener) ===")
print("Left Ctrl+Left Alt + digit  = COPY")
print("Right Ctrl+Right Alt + digit = PASTE")
print("Ctrl+C to quit.\n")

# Track exact left/right modifiers
held = set()

def _key_name(k):
    if hasattr(k, 'name'):
        return k.name.lower()
    s = str(k).lower()
    if 'ctrl' in s: return 'ctrl'
    if 'alt' in s: return 'alt'
    if 'shift' in s: return 'shift'
    return s

def on_press(key):
    try:
        name = _key_name(key)
        if 'ctrl' in name:
            if 'left' in str(key).lower() or 'ctrl_l' in str(key):
                held.add('ctrl_l')
            elif 'right' in str(key).lower() or 'ctrl_r' in str(key):
                held.add('ctrl_r')
            else:
                held.add('ctrl')
        elif 'alt' in name:
            if 'left' in str(key).lower() or 'alt_l' in str(key):
                held.add('alt_l')
            elif 'right' in str(key).lower() or 'alt_r' in str(key):
                held.add('alt_r')
            else:
                held.add('alt')
        else:
            # Check for digit
            try:
                if hasattr(key, 'char') and key.char and key.char.isdigit():
                    digit = key.char
                    slot = 10 if digit == '0' else int(digit)
                    do_action(slot)
            except:
                pass
    except Exception as e:
        print(f"press err: {e}")

def on_release(key):
    try:
        name = _key_name(key)
        if 'ctrl_l' in str(key).lower() or ( 'ctrl' in name and 'left' in str(key).lower() ):
            held.discard('ctrl_l')
        elif 'ctrl_r' in str(key).lower() or ( 'ctrl' in name and 'right' in str(key).lower() ):
            held.discard('ctrl_r')
        elif 'ctrl' in name:
            held.discard('ctrl')
        if 'alt_l' in str(key).lower() or ( 'alt' in name and 'left' in str(key).lower() ):
            held.discard('alt_l')
        elif 'alt_r' in str(key).lower() or ( 'alt' in name and 'right' in str(key).lower() ):
            held.discard('alt_r')
        elif 'alt' in name:
            held.discard('alt')
    except Exception as e:
        print(f"release err: {e}")

def release_mods():
    for k in ('ctrl','ctrl_l','ctrl_r','alt','alt_l','alt_r','shift'):
        try: pyautogui.keyUp(k)
        except: pass
    time.sleep(0.06)

def do_action(slot):
    has_left_ctrl  = 'ctrl_l' in held
    has_right_ctrl = 'ctrl_r' in held
    has_left_alt   = 'alt_l' in held
    has_right_alt  = 'alt_r' in held

    print(f"Combo detected: held={held} → slot={slot}")

    if has_left_ctrl and has_left_alt:
        # COPY
        release_mods()
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.15)
        content = pyperclip.paste()
        print(f"[COPY {slot}] captured: {content[:65]!r}")
        subprocess.run(['notify-send', '-t', '1200', 'COPY', f'Slot {slot}'], check=False)

    elif has_right_ctrl and has_right_alt:
        # PASTE
        content = f"PASTE-TEST-SLOT-{slot}-{int(time.time())}"
        pyperclip.copy(content)
        time.sleep(0.06)
        release_mods()
        pyautogui.hotkey('ctrl', 'v')
        print(f"[PASTE {slot}] injected test string")
        subprocess.run(['notify-send', '-t', '1200', 'PASTE', f'Slot {slot}'], check=False)
    else:
        print(f"  (no matching copy or paste combo for slot {slot})")

listener = pkb.Listener(on_press=on_press, on_release=on_release)
listener.start()
print("Raw listener armed. Test LCtrl+LAlt+digit and RCtrl+RAlt+digit now.\n")
try:
    listener.join()
except KeyboardInterrupt:
    listener.stop()
    print("Stopped.")
