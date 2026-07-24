#!/usr/bin/env python3
"""
RAW MODIFIER DIAGNOSTIC
Run this, then press the combos exactly:
  Left Ctrl + Left Alt + 3
  Right Ctrl + Right Alt + 3
  etc.

It will print EVERY key event with exact repr so we can see what pynput actually sees
for left vs right modifiers on your machine as root.

Ctrl+C to quit.
"""
from pynput import keyboard as pkb
import time

print("=== RAW MODIFIER SNIFFER ===")
print("Press your Left Ctrl+Alt combos and Right Ctrl+Alt combos.")
print("Watch exactly what gets printed for each modifier.\n")

pressed = set()

def on_press(key):
    try:
        name = key.name if hasattr(key, 'name') else str(key)
        print(f"[PRESS] {repr(key)}  name={name}  vk={getattr(key, 'vk', None)}")
        pressed.add(key)
    except Exception as e:
        print(f"[PRESS ERROR] {e}")

def on_release(key):
    try:
        name = key.name if hasattr(key, 'name') else str(key)
        print(f"[RELEASE] {repr(key)}  name={name}")
        pressed.discard(key)
        # Quick summary of current combo
        ctrls = [k for k in pressed if 'ctrl' in str(k).lower()]
        alts  = [k for k in pressed if 'alt' in str(k).lower()]
        if ctrls or alts:
            print(f"   currently held modifiers → ctrls: {ctrls}  alts: {alts}\n")
    except Exception as e:
        print(f"[RELEASE ERROR] {e}")

listener = pkb.Listener(on_press=on_press, on_release=on_release)
listener.start()
print("Sniffer armed. Hit the combos now.\n")
try:
    listener.join()
except KeyboardInterrupt:
    listener.stop()
    print("\nSniffer stopped.")
