import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable
import pyperclip
from .diff_manager import DiffManager
from .diff_types import DiffResult, DiffType

class DiffInterface(ttk.Frame):
    def __init__(self, parent, clipboard_manager=None):
        super().__init__(parent)
        self.clipboard_manager = clipboard_manager
        self.diff_manager = DiffManager()
        self.current_diff_result: Optional[DiffResult] = None
        
        # Callbacks
        self.status_callback: Optional[Callable] = None
        
        self._create_ui()
    
    def _create_ui(self):
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Top toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill='x', pady=(0, 5))
        
        # View mode selection
        ttk.Label(toolbar, text="View:").pack(side='left')
        
        self.view_mode = tk.StringVar(value="side_by_side")
        ttk.Radiobutton(toolbar, text="Side by Side", variable=self.view_mode,
                       value="side_by_side", command=self._refresh_diff_display).pack(side='left', padx=5)
        ttk.Radiobutton(toolbar, text="Unified", variable=self.view_mode,
                       value="unified", command=self._refresh_diff_display).pack(side='left')
        
        # Action buttons
        btn_frame = ttk.Frame(toolbar)
        btn_frame.pack(side='right')
        
        ttk.Button(btn_frame, text="Compare", command=self._perform_diff).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Clear", command=self._clear_all).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Save Result", command=self._save_result).pack(side='left', padx=2)
        
        # Input section
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill='both', expand=True)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(input_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Input tab
        self.input_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.input_tab, text="Input")
        
        # Result tab
        self.result_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.result_tab, text="Diff Result")
        
        self._create_input_tab()
        self._create_result_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready for comparison")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief='sunken', anchor='w')
        status_bar.pack(fill='x', pady=(5, 0))
    
    def _create_input_tab(self):
        # Create two-panel input interface
        paned = ttk.PanedWindow(self.input_tab, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel
        left_frame = ttk.LabelFrame(paned, text="Text 1", padding=5)
        paned.add(left_frame, weight=1)
        
        # Left panel controls
        left_controls = ttk.Frame(left_frame)
        left_controls.pack(fill='x', pady=(0, 5))
        
        ttk.Button(left_controls, text="Load from Slot", 
                  command=lambda: self._load_from_slot('left')).pack(side='left')
        ttk.Button(left_controls, text="Paste", 
                  command=lambda: self._paste_content('left')).pack(side='left', padx=5)
        ttk.Button(left_controls, text="Clear", 
                  command=lambda: self._clear_panel('left')).pack(side='left')
        
        # Left text area
        left_text_frame = ttk.Frame(left_frame)
        left_text_frame.pack(fill='both', expand=True)
        
        self.left_text = tk.Text(left_text_frame, wrap='none', font=('Consolas', 10))
        left_scroll_v = ttk.Scrollbar(left_text_frame, orient='vertical', 
                                     command=self.left_text.yview)
        left_scroll_h = ttk.Scrollbar(left_text_frame, orient='horizontal', 
                                     command=self.left_text.xview)
        
        self.left_text.configure(yscrollcommand=left_scroll_v.set, 
                                xscrollcommand=left_scroll_h.set)
        
        self.left_text.grid(row=0, column=0, sticky='nsew')
        left_scroll_v.grid(row=0, column=1, sticky='ns')
        left_scroll_h.grid(row=1, column=0, sticky='ew')
        
        left_text_frame.grid_rowconfigure(0, weight=1)
        left_text_frame.grid_columnconfigure(0, weight=1)
        
        # Right panel
        right_frame = ttk.LabelFrame(paned, text="Text 2", padding=5)
        paned.add(right_frame, weight=1)
        
        # Right panel controls
        right_controls = ttk.Frame(right_frame)
        right_controls.pack(fill='x', pady=(0, 5))
        
        ttk.Button(right_controls, text="Load from Slot", 
                  command=lambda: self._load_from_slot('right')).pack(side='left')
        ttk.Button(right_controls, text="Paste", 
                  command=lambda: self._paste_content('right')).pack(side='left', padx=5)
        ttk.Button(right_controls, text="Clear", 
                  command=lambda: self._clear_panel('right')).pack(side='left')
        
        # Right text area
        right_text_frame = ttk.Frame(right_frame)
        right_text_frame.pack(fill='both', expand=True)
        
        self.right_text = tk.Text(right_text_frame, wrap='none', font=('Consolas', 10))
        right_scroll_v = ttk.Scrollbar(right_text_frame, orient='vertical', 
                                      command=self.right_text.yview)
        right_scroll_h = ttk.Scrollbar(right_text_frame, orient='horizontal', 
                                      command=self.right_text.xview)
        
        self.right_text.configure(yscrollcommand=right_scroll_v.set, 
                                 xscrollcommand=right_scroll_h.set)
        
        self.right_text.grid(row=0, column=0, sticky='nsew')
        right_scroll_v.grid(row=0, column=1, sticky='ns')
        right_scroll_h.grid(row=1, column=0, sticky='ew')
        
        right_text_frame.grid_rowconfigure(0, weight=1)
        right_text_frame.grid_columnconfigure(0, weight=1)
    
    def _create_result_tab(self):
        # Diff result display area
        result_frame = ttk.Frame(self.result_tab)
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Stats display
        self.stats_var = tk.StringVar(value="No comparison performed")
        stats_label = ttk.Label(result_frame, textvariable=self.stats_var, 
                               font=('Arial', 10, 'bold'))
        stats_label.pack(pady=(0, 5))
        
        # Result text area
        self.result_text = tk.Text(result_frame, wrap='none', font=('Consolas', 9))
        result_scroll_v = ttk.Scrollbar(result_frame, orient='vertical', 
                                       command=self.result_text.yview)
        result_scroll_h = ttk.Scrollbar(result_frame, orient='horizontal', 
                                       command=self.result_text.xview)
        
        self.result_text.configure(yscrollcommand=result_scroll_v.set, 
                                  xscrollcommand=result_scroll_h.set)
        
        self.result_text.pack(side='left', fill='both', expand=True)
        result_scroll_v.pack(side='right', fill='y')
        result_scroll_h.pack(side='bottom', fill='x')
        
        # Configure text tags for highlighting
        self.result_text.tag_configure('equal', background='white')
        self.result_text.tag_configure('insert', background='#d4edda', foreground='#155724')
        self.result_text.tag_configure('delete', background='#f8d7da', foreground='#721c24')
        self.result_text.tag_configure('replace', background='#fff3cd', foreground='#856404')
    
    def _load_from_slot(self, panel: str):
        """Load content from clipboard slot"""
        if not self.clipboard_manager:
            messagebox.showwarning("Warning", "Clipboard manager not available")
            return
        
        # Create slot selection dialog
        slot_dialog = tk.Toplevel(self)
        slot_dialog.title("Select Slot")
        slot_dialog.geometry("300x400")
        slot_dialog.transient(self)
        slot_dialog.grab_set()
        
        ttk.Label(slot_dialog, text="Select a slot to load:", 
                 font=('Arial', 11, 'bold')).pack(pady=10)
        
        # Slot listbox
        listbox_frame = ttk.Frame(slot_dialog)
        listbox_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        slot_listbox = tk.Listbox(listbox_frame, font=('Consolas', 9))
        slot_scroll = ttk.Scrollbar(listbox_frame, orient='vertical', 
                                   command=slot_listbox.yview)
        
        slot_listbox.configure(yscrollcommand=slot_scroll.set)
        slot_listbox.pack(side='left', fill='both', expand=True)
        slot_scroll.pack(side='right', fill='y')
        
        # Populate slots
        for i in range(10):
            content = self.clipboard_manager.get_slot_content(i)
            preview = content[:50] + "..." if content and len(content) > 50 else content or "(empty)"
            slot_listbox.insert('end', f"Slot {i}: {preview}")
        
        def load_selected():
            selection = slot_listbox.curselection()
            if selection:
                slot_id = selection[0]
                content = self.clipboard_manager.get_slot_content(slot_id)
                if content:
                    target_text = self.left_text if panel == 'left' else self.right_text
                    target_text.delete('1.0', 'end')
                    target_text.insert('1.0', content)
                    self._update_status(f"Loaded content from slot {slot_id} to {panel} panel")
                slot_dialog.destroy()
        
        ttk.Button(slot_dialog, text="Load", command=load_selected).pack(pady=5)
        ttk.Button(slot_dialog, text="Cancel", command=slot_dialog.destroy).pack()
    
    def _paste_content(self, panel: str):
        """Paste content from system clipboard"""
        try:
            content = pyperclip.paste()
            target_text = self.left_text if panel == 'left' else self.right_text
            target_text.delete('1.0', 'end')
            target_text.insert('1.0', content)
            self._update_status(f"Pasted content to {panel} panel")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste content: {str(e)}")
    
    def _clear_panel(self, panel: str):
        """Clear content from specified panel"""
        target_text = self.left_text if panel == 'left' else self.right_text
        target_text.delete('1.0', 'end')
        self._update_status(f"Cleared {panel} panel")
    
    def _clear_all(self):
        """Clear all panels and results"""
        self.left_text.delete('1.0', 'end')
        self.right_text.delete('1.0', 'end')
        self.result_text.delete('1.0', 'end')
        self.current_diff_result = None
        self.stats_var.set("No comparison performed")
        self._update_status("All content cleared")
    
    def _perform_diff(self):
        """Perform diff comparison"""
        text1 = self.left_text.get('1.0', 'end-1c')
        text2 = self.right_text.get('1.0', 'end-1c')
        
        if not text1.strip() and not text2.strip():
            messagebox.showwarning("Warning", "Both panels are empty")
            return
        
        try:
            self._update_status("Calculating differences...")
            self.current_diff_result = self.diff_manager.calculate_diff(text1, text2)
            
            # Update stats
            stats_text = self.diff_manager.get_diff_stats(self.current_diff_result)
            self.stats_var.set(stats_text)
            
            # Display results
            self._refresh_diff_display()
            
            # Switch to result tab
            self.notebook.select(self.result_tab)
            
            self._update_status("Diff comparison completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate diff: {str(e)}")
            self._update_status("Diff calculation failed")
    
    def _refresh_diff_display(self):
        """Refresh the diff display based on current view mode"""
        if not self.current_diff_result:
            return
        
        self.result_text.delete('1.0', 'end')
        
        if self.view_mode.get() == "unified":
            self._display_unified_diff()
        else:
            self._display_side_by_side_diff()
    
    def _display_unified_diff(self):
        """Display unified diff format"""
        unified_diff = self.current_diff_result.unified_diff
        self.result_text.insert('1.0', unified_diff)
        
        # Apply basic highlighting for unified diff
        lines = unified_diff.split('\n')
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            line_end = f"{i+1}.end"
            
            if line.startswith('+') and not line.startswith('+++'):
                self.result_text.tag_add('insert', line_start, line_end)
            elif line.startswith('-') and not line.startswith('---'):
                self.result_text.tag_add('delete', line_start, line_end)
            elif line.startswith('@@'):
                self.result_text.tag_add('replace', line_start, line_end)
    
    def _display_side_by_side_diff(self):
        """Display side-by-side diff format"""
        for diff_line in self.current_diff_result.lines:
            line_start = self.result_text.index('end-1c')
            
            # Format line numbers
            left_num = str(diff_line.line_num_left) if diff_line.line_num_left else " "
            right_num = str(diff_line.line_num_right) if diff_line.line_num_right else " "
            
            # Format content
            left_content = diff_line.content_left[:80] if diff_line.content_left else ""
            right_content = diff_line.content_right[:80] if diff_line.content_right else ""
            
            # Create display line
            display_line = f"{left_num:>4} | {left_content:<80} | {right_num:>4} | {right_content}\n"
            
            self.result_text.insert('end', display_line)
            
            # Apply highlighting
            line_end = self.result_text.index('end-1c')
            tag_name = diff_line.diff_type.value
            self.result_text.tag_add(tag_name, line_start, line_end)
    
    def _save_result(self):
        """Save diff result to clipboard slot"""
        if not self.current_diff_result:
            messagebox.showwarning("Warning", "No diff result to save")
            return
        
        if not self.clipboard_manager:
            messagebox.showwarning("Warning", "Clipboard manager not available")
            return
        
        # Get current result text
        result_content = self.result_text.get('1.0', 'end-1c')
        
        # Create slot selection dialog
        slot_dialog = tk.Toplevel(self)
        slot_dialog.title("Save to Slot")
        slot_dialog.geometry("300x200")
        slot_dialog.transient(self)
        slot_dialog.grab_set()
        
        ttk.Label(slot_dialog, text="Select slot to save diff result:", 
                 font=('Arial', 11, 'bold')).pack(pady=10)
        
        slot_var = tk.IntVar(value=0)
        for i in range(10):
            ttk.Radiobutton(slot_dialog, text=f"Slot {i}", 
                           variable=slot_var, value=i).pack(anchor='w', padx=20)
        
        def save_to_slot():
            slot_id = slot_var.get()
            success = self.clipboard_manager.store_in_slot(slot_id, result_content)
            if success:
                self._update_status(f"Diff result saved to slot {slot_id}")
                messagebox.showinfo("Success", f"Diff result saved to slot {slot_id}")
            else:
                messagebox.showerror("Error", "Failed to save diff result")
            slot_dialog.destroy()
        
        ttk.Button(slot_dialog, text="Save", command=save_to_slot).pack(pady=10)
        ttk.Button(slot_dialog, text="Cancel", command=slot_dialog.destroy).pack()
    
    def _update_status(self, message: str):
        """Update status message"""
        self.status_var.set(message)
        if self.status_callback:
            self.status_callback(message)
    
    def set_status_callback(self, callback: Callable):
        """Set status update callback"""
        self.status_callback = callback