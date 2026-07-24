"""
History Panel - Integrated clipman history view for MultiClip GUI.
Shows clipman entries directly in the main window.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional, Set


class HistoryItem(ttk.Frame):
    """Single history entry display."""
    
    def __init__(self, parent, entry, index: int, on_select: Callable, 
                 on_double_click: Optional[Callable] = None):
        super().__init__(parent)
        self.entry = entry
        self.index = index
        self.on_select = on_select
        self.on_double_click = on_double_click
        self.selected = False
        self.order_num = None
        
        self._create_widgets()
        self._bind_events()
        
    def _create_widgets(self):
        # Selection checkbox
        self.var_selected = tk.BooleanVar(value=False)
        self.checkbox = ttk.Checkbutton(self, variable=self.var_selected, 
                                        command=self._on_checkbox_toggle)
        self.checkbox.pack(side='left', padx=(5, 0))
        
        # Index label
        self.idx_label = ttk.Label(self, text=f"{self.index:4d}", 
                                   font=('Consolas', 9), width=5)
        self.idx_label.pack(side='left', padx=(5, 0))
        
        # Order label (for ordered deployment)
        self.order_label = ttk.Label(self, text="", font=('Consolas', 9, 'bold'),
                                     width=4, foreground='blue')
        self.order_label.pack(side='left')
        
        # Preview text
        self.preview_label = ttk.Label(self, text=self.entry.preview[:60],
                                       font=('Arial', 9), wraplength=400,
                                       justify='left', anchor='w')
        self.preview_label.pack(side='left', fill='x', expand=True, padx=5)
        
        # Word count
        self.count_label = ttk.Label(self, text=f"{self.entry.word_count}w",
                                     font=('Arial', 8), foreground='gray',
                                     width=8)
        self.count_label.pack(side='right', padx=5)
        
    def _bind_events(self):
        self.bind('<Button-1>', self._on_click)
        self.preview_label.bind('<Button-1>', self._on_click)
        self.idx_label.bind('<Button-1>', self._on_click)
        self.bind('<Double-Button-1>', self._on_double_click)
        self.preview_label.bind('<Double-Button-1>', self._on_double_click)
        
    def _on_click(self, event):
        self.on_select(self.index)
        
    def _on_double_click(self, event):
        if self.on_double_click:
            self.on_double_click(self.index)
            
    def _on_checkbox_toggle(self):
        self.selected = self.var_selected.get()
        self.on_select(self.index, toggle=True)
        
    def set_selected(self, selected: bool):
        self.selected = selected
        self.var_selected.set(selected)
        if selected:
            self.configure(style='Selected.TFrame')
            self.preview_label.configure(background='#e0f0ff')
        else:
            self.configure(style='TFrame')
            self.preview_label.configure(background='')
            
    def set_order(self, order_num: Optional[int]):
        self.order_num = order_num
        if order_num:
            self.order_label.configure(text=f"[{order_num}]")
        else:
            self.order_label.configure(text="")


class HistoryPanel(ttk.Frame):
    """
    Main history panel showing clipman entries.
    Integrates directly into MultiClip GUI.
    """
    
    def __init__(self, parent, parser, on_deploy: Callable, 
                 on_select_for_slot: Optional[Callable] = None):
        super().__init__(parent)
        self.parser = parser
        self.on_deploy = on_deploy
        self.on_select_for_slot = on_select_for_slot
        
        self.entries = []
        self.history_items: List[HistoryItem] = []
        self.selected_indices: Set[int] = set()
        self.ordered_indices: dict = {}  # index -> order number
        self.current_page = 0
        self.page_size = 50
        self.mode = "select"  # "select" or "order"
        self.last_order = 0
        
        self._create_widgets()
        self.load_history()
        
    def _create_widgets(self):
        # Header
        header = ttk.Frame(self)
        header.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(header, text="Clipboard History", 
                 font=('Arial', 12, 'bold')).pack(side='left')
        
        self.count_label = ttk.Label(header, text="0 entries", 
                                     font=('Arial', 10))
        self.count_label.pack(side='left', padx=10)
        
        # Search box
        search_frame = ttk.Frame(header)
        search_frame.pack(side='right')
        
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, 
                                      width=20)
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search())
        ttk.Button(search_frame, text="Go", command=self.search).pack(side='left')
        
        # Canvas with scrollbar for history items
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(self.canvas_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical",
                                       command=self.canvas.yview)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Frame inside canvas for items
        self.items_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.items_frame,
                                                       anchor='nw', width=580)
        
        self.items_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Mouse wheel scrolling
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        
        # Footer with controls
        footer = ttk.Frame(self)
        footer.pack(fill='x', padx=5, pady=5)
        
        # Page navigation
        self.page_label = ttk.Label(footer, text="Page 1/1")
        self.page_label.pack(side='left')
        
        ttk.Button(footer, text="◀ Prev", command=self.prev_page).pack(side='left', padx=5)
        ttk.Button(footer, text="Next ▶", command=self.next_page).pack(side='left')
        
        # Mode toggle
        self.mode_btn = ttk.Button(footer, text="Mode: Select", 
                                   command=self.toggle_mode)
        self.mode_btn.pack(side='left', padx=20)
        
        # Selection info
        self.selection_label = ttk.Label(footer, text="0 selected", 
                                         font=('Arial', 10, 'bold'))
        self.selection_label.pack(side='left', padx=10)
        
        # Action buttons
        btn_frame = ttk.Frame(footer)
        btn_frame.pack(side='right')
        
        ttk.Button(btn_frame, text="Clear Selection", 
                  command=self.clear_selection).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Deploy to Slots", 
                  command=self.deploy_selection).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Refresh", 
                  command=self.load_history).pack(side='left', padx=2)
        
        # Help text
        help_frame = ttk.LabelFrame(self, text="Help", padding=5)
        help_frame.pack(fill='x', padx=5, pady=5)
        
        help_text = ("Click to select • Double-click to copy to clipboard • "
                    "Space: toggle select • 1-9: set order • "
                    "Deploy loads selected items into slots 1-N")
        ttk.Label(help_frame, text=help_text, font=('Arial', 8), 
                 wraplength=550).pack()
        
    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def load_history(self):
        """Load history entries from parser."""
        self.entries = self.parser.parse(max_entries=500)
        self.current_page = 0
        self._update_display()
        self.count_label.configure(text=f"{len(self.entries)} entries")
        
    def search(self):
        """Search history."""
        query = self.search_var.get().strip()
        if query:
            self.entries = self.parser.search(query, max_results=200)
        else:
            self.entries = self.parser.parse(max_entries=500)
        self.current_page = 0
        self._update_display()
        self.count_label.configure(text=f"{len(self.entries)} entries (search)")
        
    def _update_display(self):
        """Update the display with current page of entries."""
        # Clear existing items
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        self.history_items = []
        
        # Calculate page range
        start = self.current_page * self.page_size
        end = min(start + self.page_size, len(self.entries))
        page_entries = self.entries[start:end]
        
        # Create history items
        for i, entry in enumerate(page_entries):
            actual_index = start + i
            item = HistoryItem(self.items_frame, entry, actual_index,
                              self._on_item_select, self._on_item_double_click)
            item.pack(fill='x', pady=1)
            
            # Restore selection state
            if actual_index in self.selected_indices:
                item.set_selected(True)
            if actual_index in self.ordered_indices:
                item.set_order(self.ordered_indices[actual_index])
                
            self.history_items.append(item)
            
        # Update page label
        total_pages = max(1, (len(self.entries) + self.page_size - 1) // self.page_size)
        self.page_label.configure(text=f"Page {self.current_page + 1}/{total_pages}")
        
    def _on_item_select(self, index, toggle=False):
        """Handle item selection."""
        if self.mode == "order" and not toggle:
            # In order mode, clicking assigns order numbers
            if index not in self.selected_indices:
                self.selected_indices.add(index)
                self.last_order += 1
                self.ordered_indices[index] = self.last_order
            else:
                # Already selected, ignore or reassign?
                pass
        else:
            # Normal toggle
            if index in self.selected_indices:
                self.selected_indices.remove(index)
                if index in self.ordered_indices:
                    del self.ordered_indices[index]
            else:
                self.selected_indices.add(index)
                
        self._update_selection_label()
        self._update_display()
        
    def _on_item_double_click(self, index):
        """Handle double-click - copy to clipboard."""
        if index < len(self.entries):
            entry = self.entries[index]
            import pyperclip
            pyperclip.copy(entry.get_display_text())
            
    def toggle_mode(self):
        """Toggle between select and order mode."""
        if self.mode == "select":
            self.mode = "order"
            self.mode_btn.configure(text="Mode: Order (1-9)")
            self.last_order = 0
        else:
            self.mode = "select"
            self.mode_btn.configure(text="Mode: Select")
            self.ordered_indices.clear()
            self.last_order = 0
        self._update_display()
        
    def clear_selection(self):
        """Clear all selections."""
        self.selected_indices.clear()
        self.ordered_indices.clear()
        self.last_order = 0
        self._update_selection_label()
        self._update_display()
        
    def _update_selection_label(self):
        """Update selection counter."""
        count = len(self.selected_indices)
        if self.ordered_indices:
            self.selection_label.configure(text=f"{count} selected (ordered)")
        else:
            self.selection_label.configure(text=f"{count} selected")
            
    def deploy_selection(self):
        """Deploy selected items to slots."""
        if not self.selected_indices:
            return
            
        # Get selected entries in order
        if self.ordered_indices:
            # Use custom order
            sorted_pairs = sorted(self.ordered_indices.items(), key=lambda x: x[1])
            selected_entries = [self.entries[idx] for idx, _ in sorted_pairs 
                               if idx < len(self.entries)]
        else:
            # Use index order
            selected_entries = [self.entries[idx] for idx in sorted(self.selected_indices)
                               if idx < len(self.entries)]
                               
        # Call deploy callback
        if self.on_deploy:
            self.on_deploy(selected_entries)
            
    def prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self._update_display()
            
    def next_page(self):
        """Go to next page."""
        total_pages = (len(self.entries) + self.page_size - 1) // self.page_size
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self._update_display()
            
    def get_selected_entries(self):
        """Get list of selected entry objects."""
        return [self.entries[idx] for idx in self.selected_indices 
                if idx < len(self.entries)]
