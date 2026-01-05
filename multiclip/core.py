import pyperclip
import pyautogui
import time
import json
import os
from pathlib import Path

class MultiClipCore:
    def __init__(self, slots_file="clipboard_dict.json", max_slots=10):
        self.max_slots = max_slots
        # Ensure we look in the project root for the json (one level up from this file)
        self.slots_file = Path(__file__).parent.parent / slots_file
        self.slots = self._load_slots()
        self.paste_order = list(range(1, max_slots + 1))
        
        # SEQUENTIAL STATE
        self.current_seq_slot = 1

    def _load_slots(self):
        if self.slots_file.exists():
            try:
                with open(self.slots_file) as f:
                    data = json.load(f)
                    # Clean data to ensure int keys
                    clean_data = {}
                    for k, v in data.items():
                        if str(k).isdigit():
                            clean_data[int(k)] = v
                        elif k.startswith("slot_"):
                            try:
                                idx = int(k.split("_")[1])
                                clean_data[idx] = v
                            except: pass
                    return clean_data
            except:
                pass
        return {i: "" for i in range(1, self.max_slots + 1)}

    def _save_slots(self):
        with open(self.slots_file, "w") as f:
            json.dump(self.slots, f, indent=2)

    def _release_modifiers(self):
        """Force release keys to prevent signal pollution (Ghost Keys)"""
        try:
            pyautogui.keyUp('shift')
            pyautogui.keyUp('alt')
            pyautogui.keyUp('ctrl')
        except: pass
        time.sleep(0.05)

    def copy_to_slot(self, slot: int):
        if not (1 <= slot <= self.max_slots): return None
        
        self._release_modifiers()

        # Send Copy
        try:
            os.system("xdotool key --clearmodifiers ctrl+c")
        except:
            pyautogui.hotkey("ctrl", "c")
            
        time.sleep(0.2)
        text = pyperclip.paste()
        
        if text:
            self.slots[slot] = text
            self._save_slots()
            print(f"[DEBUG] Copied to Slot {slot}")
            return text
        return None

    def paste_from_slot(self, slot: int):
        if not (1 <= slot <= self.max_slots): return
        text = self.slots.get(slot, "")
        if not text: return
        
        pyperclip.copy(text)
        time.sleep(0.1)
        
        self._release_modifiers()

        # Send Paste
        try:
            os.system("xdotool key --clearmodifiers ctrl+v")
        except:
            pyautogui.hotkey("ctrl", "v")

    # --- SEQUENTIAL LOGIC ---
    def sequential_copy(self):
        text = self.copy_to_slot(self.current_seq_slot)
        used_slot = self.current_seq_slot
        if text:
            self.current_seq_slot += 1
            if self.current_seq_slot > self.max_slots:
                self.current_seq_slot = 1
        return used_slot, text

    def sequential_paste(self):
        # 0-based index for paste_order list
        idx = self.current_seq_slot - 1
        actual_slot = self.paste_order[idx]
        
        self.paste_from_slot(actual_slot)
        
        self.current_seq_slot += 1
        if self.current_seq_slot > self.max_slots:
            self.current_seq_slot = 1
        return actual_slot

    def clear_all(self):
        self.slots = {i: "" for i in range(1, self.max_slots + 1)}
        self._save_slots()
        self.current_seq_slot = 1
