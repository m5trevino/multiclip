import tkinter as tk
from tkinter import ttk

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MultiClip")
        self.root.geometry("600x500")
        
        self.clipboard_manager = None
        self.slot_select_callback = None
        self.mode_change_callback = None
        
        self.slots = []
        self._setup_ui()
        
    def _setup_ui(self):
        # Mode Selector
        mode_frame = ttk.LabelFrame(self.root, text="Mode Selection")
        mode_frame.pack(fill="x", padx=5, pady=5)
        
        self.mode_var = tk.StringVar(value="MultiClip")
        
        modes = [("Standard MultiClip", "MultiClip"), ("Orderly (Sequential)", "Orderly")]
        
        for text, mode in modes:
            rb = ttk.Radiobutton(mode_frame, text=text, variable=self.mode_var, 
                               value=mode, command=self._on_mode_change)
            rb.pack(side="left", padx=10)

        # Slots Display
        slots_frame = ttk.LabelFrame(self.root, text="Clipboard Slots")
        slots_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(slots_frame)
        scrollbar = ttk.Scrollbar(slots_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initialize 10 slots
        for i in range(10):
            frame = ttk.Frame(self.scrollable_frame)
            frame.pack(fill="x", pady=2)
            
            btn = ttk.Button(frame, text=f"Slot {i+1}", width=10,
                           command=lambda idx=i: self._on_slot_click(idx))
            btn.pack(side="left", padx=5)
            
            lbl = ttk.Label(frame, text="<Empty>", anchor="w")
            lbl.pack(side="left", fill="x", expand=True)
            
            self.slots.append(lbl)

    def set_clipboard_manager(self, manager):
        self.clipboard_manager = manager
        
    def set_slot_select_callback(self, callback):
        self.slot_select_callback = callback
        
    def set_mode_change_callback(self, callback):
        self.mode_change_callback = callback
        
    def update_slot(self, slot_id, full_text, preview):
        if 0 <= slot_id < len(self.slots):
            self.slots[slot_id].config(text=preview)
            
    def _on_slot_click(self, slot_index):
        # Convert 0-based index back to 1-based for callback if needed, 
        # but manager usually expects 0-based. multiclip.py expects 0-based.
        if self.slot_select_callback:
            self.slot_select_callback(slot_index)
            
    def _on_mode_change(self):
        if self.mode_change_callback:
            self.mode_change_callback(self.mode_var.get())

    def run(self):
        self.root.mainloop()
