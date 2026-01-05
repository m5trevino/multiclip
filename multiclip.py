import pyperclip
import keyboard
import json
import os
import pyautogui
import subprocess
import time
import tkinter as tk
from tkinter import ttk
import threading
from gui.main_window import MainWindow
from shared.clipboard_manager import ClipboardManager

class MultiClipSystem:
    def __init__(self):
        # Paths
        self.dict_file = "/home/flintx/multiclip/clipboard_dict.json"
        self.icon_path = "/home/flintx/multiclip/chargers.png"
        
        # Initialize managers
        self.clipboard_manager = ClipboardManager(num_slots=10)
        self.clipboard_slots = self.load_dictionary()
        
        # Mode management
        self.current_mode = "MultiClip"
        
        # Setup UI
        self.main_window = MainWindow()
        self.main_window.set_clipboard_manager(self.clipboard_manager)
        self._setup_callbacks()
        self.register_hotkeys()
        
        # Load existing clipboard data into manager
        self._sync_clipboard_data()
        
    def _setup_callbacks(self):
        """Setup callbacks between UI and system"""
        self.main_window.set_slot_select_callback(self._on_slot_select)
        self.main_window.set_mode_change_callback(self._on_mode_change)
    
    def _sync_clipboard_data(self):
        """Sync existing clipboard data with the clipboard manager"""
        for i in range(10):
            slot_key = f"slot_{i+1}"
            if slot_key in self.clipboard_slots:
                content = self.clipboard_slots[slot_key]
                self.clipboard_manager.store_in_slot(i, content)
                preview = content[:50] + "..." if len(content) > 50 else content
                self.main_window.update_slot(i, content, preview)
    
    def _on_slot_select(self, slot_id: int):
        """Handle slot selection from UI"""
        content = self.clipboard_manager.get_slot_content(slot_id)
        if content:
            pyperclip.copy(content)
            self.show_toast("Slot Copied", f"Slot {slot_id} copied to clipboard")
    
    def _on_mode_change(self, new_mode: str):
        """Handle mode change from UI"""
        self.current_mode = new_mode
        self.show_toast(f"{new_mode} Mode", f"{new_mode} mode activated")
    
    def load_dictionary(self):
        """Load clipboard slots from file"""
        if os.path.exists(self.dict_file):
            with open(self.dict_file, "r") as file:
                return json.load(file)
        else:
            return {f"slot_{i}": "" for i in range(1, 16)}
    
    def save_dictionary(self):
        """Save clipboard slots to file"""
        with open(self.dict_file, "w") as file:
            json.dump(self.clipboard_slots, file, indent=4)
    
    def show_toast(self, title, message):
        """Show system notification with custom icon"""
        try:
            subprocess.run([
                "notify-send", 
                "-i", self.icon_path, 
                title, 
                message, 
                "-t", "3000"
            ], check=False)
        except Exception as e:
            print(f"Toast notification error: {e}")
    
    def add_to_slot(self, slot_num):
        """Copy selected content to clipboard slot"""
        try:
            # Use your working method: simulate Ctrl+C first
            pyautogui.hotkey("ctrl", "c")
            time.sleep(0.1)  # Give it time to copy
            
            # Get the copied content
            clipboard_content = pyperclip.paste()
            
            # Normal multiclip mode
            actual_slot = slot_num - 1  # Convert to 0-based
            slot_key = f"slot_{slot_num}"
            
            self.clipboard_slots[slot_key] = clipboard_content
            self.clipboard_manager.store_in_slot(actual_slot, clipboard_content)
            self.save_dictionary()
            
            # Update UI
            preview = clipboard_content[:50] + "..." if len(clipboard_content) > 50 else clipboard_content
            self.main_window.update_slot(actual_slot, clipboard_content, preview)
            
            self.show_toast("Slot Updated", f"Slot {slot_num} updated")
            
        except Exception as e:
            self.show_toast("Copy Error", str(e))
    
    def paste_from_slot(self, slot_num):
        """Paste content from clipboard slot"""
        try:
            actual_slot = slot_num - 1  # Convert to 0-based
            content = self.clipboard_manager.get_slot_content(actual_slot)
            
            if content:
                pyperclip.copy(content)
                time.sleep(0.1)
                pyautogui.hotkey("ctrl", "v")
                
                self.show_toast("Slot Pasted", f"Slot {slot_num} content pasted")
            else:
                self.show_toast("Slot Empty", f"No content in slot {slot_num}")
                
        except Exception as e:
            self.show_toast("Paste Error", str(e))
    
    def transfer_to_default(self, slot_num):
        """Transfer slot content to default clipboard"""
        try:
            actual_slot = slot_num - 1  # Convert to 0-based
            content = self.clipboard_manager.get_slot_content(actual_slot)
            
            if content:
                pyperclip.copy(content)
                self.show_toast("Slot Transferred", f"Slot {slot_num} transferred to clipboard")
            else:
                self.show_toast("Slot Empty", f"No content in slot {slot_num}")
                
        except Exception as e:
            self.show_toast("Transfer Error", str(e))
    
    def register_hotkeys(self):
        """Register all hotkeys"""
        def hotkey_thread():
            try:
                # Copy hotkeys (Ctrl + 1-9)
                for i in range(1, 10):
                    keyboard.add_hotkey(f"ctrl+{i}", self.add_to_slot, args=[i])
                
                # Paste hotkeys (Ctrl + Shift + 1-9)
                for i in range(1, 10):
                    keyboard.add_hotkey(f"ctrl+shift+{i}", self.paste_from_slot, args=[i])
                
                # Transfer hotkeys (Ctrl + Alt + 1-9)
                for i in range(1, 10):
                    keyboard.add_hotkey(f"ctrl+alt+{i}", self.transfer_to_default, args=[i])
                
                print("All hotkeys registered successfully!")
                
            except Exception as e:
                print(f"Hotkey registration error: {e}")
        
        # Start hotkeys in background thread
        threading.Thread(target=hotkey_thread, daemon=True).start()
    
    def run(self):
        """Start the application"""
        self.show_toast("MultiClip Started", "System Ready")
        self.main_window.run()

if __name__ == "__main__":
    app = MultiClipSystem()
    app.run()
