import pyperclip
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import threading
import time

class ClipboardSlot:
    def __init__(self, slot_id: int, content: str = "", content_type: str = "text"):
        self.id = slot_id
        self.content = content
        self.timestamp = datetime.now()
        self.content_type = content_type
        self.preview = self._generate_preview()
    
    def _generate_preview(self) -> str:
        if len(self.content) <= 50:
            return self.content
        return self.content[:47] + "..."
    
    def update_content(self, content: str, content_type: str = "text"):
        self.content = content
        self.content_type = content_type
        self.timestamp = datetime.now()
        self.preview = self._generate_preview()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "content_type": self.content_type,
            "preview": self.preview
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        slot = cls(data["id"], data["content"], data["content_type"])
        slot.timestamp = datetime.fromisoformat(data["timestamp"])
        return slot

class ClipboardManager:
    def __init__(self, num_slots: int = 10):
        self.slots: Dict[int, ClipboardSlot] = {}
        self.num_slots = num_slots
        self.current_clipboard = ""
        self.monitoring = False
        self.monitor_thread = None
        self._initialize_slots()
    
    def _initialize_slots(self):
        for i in range(self.num_slots):
            self.slots[i] = ClipboardSlot(i)
    
    def store_in_slot(self, slot_id: int, content: str, content_type: str = "text") -> bool:
        if 0 <= slot_id < self.num_slots:
            self.slots[slot_id].update_content(content, content_type)
            return True
        return False
    
    def get_slot_content(self, slot_id: int) -> Optional[str]:
        if 0 <= slot_id < self.num_slots:
            return self.slots[slot_id].content
        return None
    
    def get_slot_preview(self, slot_id: int) -> Optional[str]:
        if 0 <= slot_id < self.num_slots:
            return self.slots[slot_id].preview
        return None
    
    def copy_to_slot(self, slot_id: int) -> bool:
        try:
            content = pyperclip.paste()
            return self.store_in_slot(slot_id, content)
        except Exception:
            return False
    
    def paste_from_slot(self, slot_id: int) -> bool:
        content = self.get_slot_content(slot_id)
        if content is not None:
            try:
                pyperclip.copy(content)
                return True
            except Exception:
                return False
        return False
    
    def get_all_slots_status(self) -> Dict[int, Dict[str, Any]]:
        return {slot_id: slot.to_dict() for slot_id, slot in self.slots.items()}
    
    def clear_slot(self, slot_id: int) -> bool:
        if 0 <= slot_id < self.num_slots:
            self.slots[slot_id].update_content("")
            return True
        return False
    
    def clear_all_slots(self):
        for slot_id in range(self.num_slots):
            self.clear_slot(slot_id)
    
    def save_state(self, filepath: str) -> bool:
        try:
            state = {
                "slots": {str(slot_id): slot.to_dict() for slot_id, slot in self.slots.items()},
                "timestamp": datetime.now().isoformat()
            }
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception:
            return False
    
    def load_state(self, filepath: str) -> bool:
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            for slot_id_str, slot_data in state["slots"].items():
                slot_id = int(slot_id_str)
                if 0 <= slot_id < self.num_slots:
                    self.slots[slot_id] = ClipboardSlot.from_dict(slot_data)
            return True
        except Exception:
            return False
    
    def start_monitoring(self):
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitor_clipboard(self):
        while self.monitoring:
            try:
                current = pyperclip.paste()
                if current != self.current_clipboard:
                    self.current_clipboard = current
                    # Trigger clipboard change event if needed
                time.sleep(0.1)
            except Exception:
                pass
