import pyperclip
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class ClipboardSlot:
    def __init__(self, slot_id: int, content: str = "", order: int = 0):
        self.id = slot_id
        self.content = content
        self.order = order if order > 0 else slot_id + 1
        self.timestamp = datetime.now()
        self.preview = self._generate_preview()
    
    def _generate_preview(self) -> str:
        if not self.content: return ""
        clean = self.content.replace('\n', ' ').strip()
        return clean[:47] + "..." if len(clean) > 50 else clean
    
    def update_content(self, content: str):
        self.content = content
        self.timestamp = datetime.now()
        self.preview = self._generate_preview()
    
    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "content": self.content, "order": self.order, "preview": self.preview}

class ClipboardManager:
    def __init__(self, num_slots: int = 30):
        self.slots: Dict[int, ClipboardSlot] = {i: ClipboardSlot(i) for i in range(num_slots)}
        self.num_slots = num_slots
    
    def store_in_slot(self, slot_id: int, content: str) -> bool:
        if 0 <= slot_id < self.num_slots:
            self.slots[slot_id].update_content(content)
            return True
        return False
        
    def get_slot_content(self, slot_id: int) -> Optional[str]:
        return self.slots[slot_id].content if 0 <= slot_id < self.num_slots else None
        
    def get_ordered_indices(self) -> List[int]:
        active = [s for s in self.slots.values() if s.content.strip()]
        return [s.id for s in sorted(active, key=lambda s: (s.order, s.id))]

    def clear_all_slots(self):
        for slot in self.slots.values(): slot.update_content("")
