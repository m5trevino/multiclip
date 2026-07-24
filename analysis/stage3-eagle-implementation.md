# 🦅 STAGE 3: EAGLE (Code Implementation)

## **PROJECT STRUCTURE:**
```
multiclip/
├── diff_marker/
│   ├── __init__.py
│   ├── diff_manager.py
│   ├── diff_interface.py
│   └── diff_types.py
├── gui/
│   └── main_window.py (enhanced)
├── shared/
│   ├── clipboard_manager.py (existing)
│   └── config_manager.py (existing)
└── multiclip.py (enhanced)
```

## **COMPLETE CODE FILES:**

**filename: diff_marker/__init__.py**
```python
"""
Diff-Marker module for MultiClip system
Provides text comparison and visual diff capabilities
"""

from .diff_manager import DiffManager
from .diff_interface import DiffInterface
from .diff_types import DiffResult, DiffLine, DiffType

__all__ = ['DiffManager', 'DiffInterface', 'DiffResult', 'DiffLine', 'DiffType']
```

**filename: diff_marker/diff_types.py**
```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class DiffType(Enum):
    EQUAL = "equal"
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"

@dataclass
class DiffLine:
    line_num_left: Optional[int]
    line_num_right: Optional[int]
    content_left: str
    content_right: str
    diff_type: DiffType
    
@dataclass
class DiffResult:
    lines: List[DiffLine]
    stats: dict
    unified_diff: str
    
    def __post_init__(self):
        if not self.stats:
            self.stats = self._calculate_stats()
    
    def _calculate_stats(self) -> dict:
        stats = {
            'additions': 0,
            'deletions': 0,
            'modifications': 0,
            'total_lines': len(self.lines)
        }
        
        for line in self.lines:
            if line.diff_type == DiffType.INSERT:
                stats['additions'] += 1
            elif line.diff_type == DiffType.DELETE:
                stats['deletions'] += 1
            elif line.diff_type == DiffType.REPLACE:
                stats['modifications'] += 1
                
        return stats
```

**filename: diff_marker/diff_manager.py**
```python
import difflib
from typing import List, Tuple
from .diff_types import DiffResult, DiffLine, DiffType

class DiffManager:
    def __init__(self):
        self.max_text_size = 1000000  # 1MB limit
        
    def calculate_diff(self, text1: str, text2: str, context_lines: int = 3) -> DiffResult:
        """Calculate differences between two texts"""
        
        # Validate input size
        if len(text1) > self.max_text_size or len(text2) > self.max_text_size:
            raise ValueError(f"Text size exceeds maximum limit of {self.max_text_size} characters")
        
        # Split into lines
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)
        
        # Generate unified diff
        unified_diff = '\n'.join(difflib.unified_diff(
            lines1, lines2,
            fromfile='Text 1',
            tofile='Text 2',
            n=context_lines
        ))
        
        # Generate side-by-side diff data
        diff_lines = self._generate_side_by_side_diff(lines1, lines2)
        
        return DiffResult(
            lines=diff_lines,
            stats={},  # Will be calculated in __post_init__
            unified_diff=unified_diff
        )
    
    def _generate_side_by_side_diff(self, lines1: List[str], lines2: List[str]) -> List[DiffLine]:
        """Generate side-by-side diff representation"""
        diff_lines = []
        
        # Use SequenceMatcher for detailed comparison
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Lines are identical
                for i in range(i1, i2):
                    diff_lines.append(DiffLine(
                        line_num_left=i + 1,
                        line_num_right=j1 + (i - i1) + 1,
                        content_left=lines1[i].rstrip('\n'),
                        content_right=lines2[j1 + (i - i1)].rstrip('\n'),
                        diff_type=DiffType.EQUAL
                    ))
            
            elif tag == 'delete':
                # Lines deleted from text1
                for i in range(i1, i2):
                    diff_lines.append(DiffLine(
                        line_num_left=i + 1,
                        line_num_right=None,
                        content_left=lines1[i].rstrip('\n'),
                        content_right="",
                        diff_type=DiffType.DELETE
                    ))
            
            elif tag == 'insert':
                # Lines inserted in text2
                for j in range(j1, j2):
                    diff_lines.append(DiffLine(
                        line_num_left=None,
                        line_num_right=j + 1,
                        content_left="",
                        content_right=lines2[j].rstrip('\n'),
                        diff_type=DiffType.INSERT
                    ))
            
            elif tag == 'replace':
                # Lines replaced
                max_lines = max(i2 - i1, j2 - j1)
                for k in range(max_lines):
                    left_idx = i1 + k if k < (i2 - i1) else None
                    right_idx = j1 + k if k < (j2 - j1) else None
                    
                    diff_lines.append(DiffLine(
                        line_num_left=left_idx + 1 if left_idx is not None else None,
                        line_num_right=right_idx + 1 if right_idx is not None else None,
                        content_left=lines1[left_idx].rstrip('\n') if left_idx is not None else "",
                        content_right=lines2[right_idx].rstrip('\n') if right_idx is not None else "",
                        diff_type=DiffType.REPLACE
                    ))
        
        return diff_lines
    
    def format_unified_diff(self, diff_result: DiffResult) -> str:
        """Return formatted unified diff"""
        return diff_result.unified_diff
    
    def get_diff_stats(self, diff_result: DiffResult) -> str:
        """Return formatted diff statistics"""
        stats = diff_result.stats
        return (f"Changes: +{stats['additions']} -{stats['deletions']} "
                f"~{stats['modifications']} (Total: {stats['total_lines']} lines)")
```

**filename: diff_marker/diff_interface.py**
```python
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
```

**filename: gui/main_window.py (Enhanced)**
```python
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Callable, Optional
import threading
from diff_marker.diff_interface import DiffInterface

class SlotDisplay(ttk.Frame):
    def __init__(self, parent, slot_id: int, on_select: Callable):
        super().__init__(parent)
        self.slot_id = slot_id
        self.on_select = on_select
        self.content = ""
        self.preview = ""
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Slot header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', padx=2, pady=1)
        
        self.slot_label = ttk.Label(header_frame, text=f"Slot {self.slot_id}", 
                                   font=('Arial', 9, 'bold'))
        self.slot_label.pack(side='left')
        
        self.status_label = ttk.Label(header_frame, text="Empty", 
                                     font=('Arial', 8), foreground='gray')
        self.status_label.pack(side='right')
        
        # Content preview
        self.preview_text = tk.Text(self, height=2, width=40, wrap='word',
                                   font=('Consolas', 8), state='disabled',
                                   cursor='hand2')
        self.preview_text.pack(fill='both', expand=True, padx=2, pady=1)
        
        # Bind click event
        self.preview_text.bind('<Button-1>', self._on_click)
        
        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy to Clipboard", 
                                     command=self._copy_to_clipboard)
        self.context_menu.add_command(label="Clear Slot", 
                                     command=self._clear_slot)
        
        self.preview_text.bind('<Button-3>', self._show_context_menu)
    
    def update_content(self, content: str, preview: str):
        self.content = content
        self.preview = preview
        
        # Update preview display
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, 'end')
        self.preview_text.insert(1.0, preview)
        self.preview_text.config(state='disabled')
        
        # Update status
        if content:
            self.status_label.config(text=f"{len(content)} chars", foreground='blue')
            self.preview_text.config(bg='#f0f8ff')
        else:
            self.status_label.config(text="Empty", foreground='gray')
            self.preview_text.config(bg='white')
    
    def _on_click(self, event):
        if self.content:
            self.on_select(self.slot_id)
    
    def _show_context_menu(self, event):
        if self.content:
            self.context_menu.post(event.x_root, event.y_root)
    
    def _copy_to_clipboard(self):
        if self.content:
            self.on_select(self.slot_id)
    
    def _clear_slot(self):
        # This should call back to the main manager
        pass

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MultiClip System")
        self.root.geometry("900x700")
        
        # Callbacks
        self.slot_select_callback: Optional[Callable] = None
        self.mode_change_callback: Optional[Callable] = None
        self.orderly_callback: Optional[Callable] = None
        
        self.slot_displays: Dict[int, SlotDisplay] = {}
        self.current_mode = "Multiclip"
        
        # Add clipboard manager reference
        self.clipboard_manager = None
        
        self._create_ui()
    
    def set_clipboard_manager(self, clipboard_manager):
        """Set the clipboard manager reference"""
        self.clipboard_manager = clipboard_manager
    
    def _create_ui(self):
        # Main menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save State", command=self._save_state)
        file_menu.add_command(label="Load State", command=self._load_state)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Top toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        # Mode buttons
        ttk.Label(toolbar, text="Mode:", font=('Arial', 10, 'bold')).pack(side='left')
        
        self.mode_var = tk.StringVar(value="Multiclip")
        mode_frame = ttk.Frame(toolbar)
        mode_frame.pack(side='left', padx=10)
        
        # Updated mode list to include Diff-Marker
        for mode in ["Multiclip", "Orderly", "Snippers", "Diff-Marker"]:
            btn = ttk.Radiobutton(mode_frame, text=mode, variable=self.mode_var,
                                 value=mode, command=self._on_mode_change)
            btn.pack(side='left', padx=5)
        
        # Status display
        self.status_label = ttk.Label(toolbar, text="Ready", 
                                     font=('Arial', 9), foreground='green')
        self.status_label.pack(side='right')
        
        # Main content area
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel - slot displays
        left_panel = ttk.LabelFrame(content_frame, text="Clipboard Slots", padding=5)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Create slot displays in grid
        slots_frame = ttk.Frame(left_panel)
        slots_frame.pack(fill='both', expand=True)
        
        for i in range(10):
            row = i // 2
            col = i % 2
            
            slot_display = SlotDisplay(slots_frame, i, self._on_slot_select)
            slot_display.grid(row=row, column=col, sticky='nsew', 
                             padx=2, pady=2)
            
            self.slot_displays[i] = slot_display
        
        # Configure grid weights
        for i in range(5):  # 5 rows
            slots_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):  # 2 columns
            slots_frame.grid_columnconfigure(i, weight=1)
        
        # Right panel - mode-specific controls
        self.right_panel = ttk.LabelFrame(content_frame, text="Controls", padding=5)
        self.right_panel.pack(side='right', fill='both', padx=(5, 0))
        
        self._create_mode_panels()
        
        # Bottom status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill='x', padx=5, pady=5)
        
        self.bottom_status = ttk.Label(status_frame, text="MultiClip System Ready", 
                                      relief='sunken', anchor='w')
        self.bottom_status.pack(fill='x')
    
    def _create_mode_panels(self):
        # Multiclip panel
        self.multiclip_panel = ttk.Frame(self.right_panel)
        
        ttk.Label(self.multiclip_panel, text="Multiclip Mode", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        ttk.Button(self.multiclip_panel, text="Clear All Slots",
                  command=self._clear_all_slots).pack(pady=5)
        
        ttk.Separator(self.multiclip_panel, orient='horizontal').pack(fill='x', pady=10)
        
        help_text = """Hotkeys:
Ctrl+0-9: Copy to slot
Ctrl+Shift+0-9: Paste from slot
Ctrl+Alt+0-9: Transfer to clipboard"""
        
        ttk.Label(self.multiclip_panel, text=help_text, 
                 font=('Arial', 9), justify='left').pack(pady=5)
        
        # Orderly panel
        self.orderly_panel = ttk.Frame(self.right_panel)
        
        ttk.Label(self.orderly_panel, text="Orderly Mode", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        self.orderly_status = ttk.Label(self.orderly_panel, text="Inactive", 
                                       font=('Arial', 10), foreground='gray')
        self.orderly_status.pack(pady=5)
        
        btn_frame = ttk.Frame(self.orderly_panel)
        btn_frame.pack(pady=10)
        
        self.orderly_toggle_btn = ttk.Button(btn_frame, text="Activate Orderly",
                                           command=self._toggle_orderly)
        self.orderly_toggle_btn.pack(pady=2)
        
        ttk.Button(btn_frame, text="Reset Sequence",
                  command=self._reset_orderly).pack(pady=2)
        
        # Snippers panel
        self.snippers_panel = ttk.Frame(self.right_panel)
        
        ttk.Label(self.snippers_panel, text="Snippers Mode", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        ttk.Button(self.snippers_panel, text="View Snippets",
                  command=self._open_snippers_view).pack(pady=5)
        
        ttk.Button(self.snippers_panel, text="Save New Snippet",
                  command=self._open_snippers_save).pack(pady=5)
        
        # NEW: Diff-Marker panel
        self.diff_marker_panel = ttk.Frame(self.right_panel)
        
        ttk.Label(self.diff_marker_panel, text="Diff-Marker Mode", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Create the diff interface
        self.diff_interface = DiffInterface(self.diff_marker_panel, self.clipboard_manager)
        self.diff_interface.pack(fill='both', expand=True)
        
        # Set up status callback
        self.diff_interface.set_status_callback(self.update_status)
        
        # Show initial panel
        self._show_mode_panel("Multiclip")
    
    def _show_mode_panel(self, mode: str):
        # Hide all panels
        for panel in [self.multiclip_panel, self.orderly_panel, 
                     self.snippers_panel, self.diff_marker_panel]:
            panel.pack_forget()
        
        # Show selected panel
        if mode == "Multiclip":
            self.multiclip_panel.pack(fill='both', expand=True)
        elif mode == "Orderly":
            self.orderly_panel.pack(fill='both', expand=True)
        elif mode == "Snippers":
            self.snippers_panel.pack(fill='both', expand=True)
        elif mode == "Diff-Marker":
            # Update clipboard manager reference if needed
            if self.clipboard_manager:
                self.diff_interface.clipboard_manager = self.clipboard_manager
            self.diff_marker_panel.pack(fill='both', expand=True)
    
    def _on_mode_change(self):
        new_mode = self.mode_var.get()
        if new_mode != self.current_mode:
            self.current_mode = new_mode
            self._show_mode_panel(new_mode)
            
            if self.mode_change_callback:
                self.mode_change_callback(new_mode)
    
    def _on_slot_select(self, slot_id: int):
        if self.slot_select_callback:
            self.slot_select_callback(slot_id)
    
    def _toggle_orderly(self):
        if self.orderly_callback:
            self.orderly_callback("toggle")
    
    def _reset_orderly(self):
        if self.orderly_callback:
            self.orderly_callback("reset")
    
    def _clear_all_slots(self):
        if messagebox.askyesno("Confirm", "Clear all clipboard slots?"):
            # This should call back to the main manager
            pass
    
    def _save_state(self):
        # Implement state saving
        pass
    
    def _load_state(self):
        # Implement state loading
        pass
    
    def _open_snippers_view(self):
        # Launch snippers view window
        pass
    
    def _open_snippers_save(self):
        # Launch snippers save window
        pass
    
    # Public interface methods
    def update_slot(self, slot_id: int, content: str, preview: str):
        if slot_id in self.slot_displays:
            self.slot_displays[slot_id].update_content(content, preview)
    
    def update_status(self, status: str, color: str = 'black'):
        self.status_label.config(text=status, foreground=color)
    
    def update_bottom_status(self, status: str):
        self.bottom_status.config(text=status)
    
    def update_orderly_status(self, status: str, active: bool):
        self.orderly_status.config(text=status, 
                                  foreground='green' if active else 'gray')
        self.orderly_toggle_btn.config(text="Deactivate Orderly" if active else "Activate Orderly")
    
    def set_slot_select_callback(self, callback: Callable):
        self.slot_select_callback = callback
    
    def set_mode_change_callback(self, callback: Callable):
        self.mode_change_callback = callback
    
    def set_orderly_callback(self, callback: Callable):
        self.orderly_callback = callback
    
    def run(self):
        self.root.mainloop()
    
    def destroy(self):
        self.root.destroy()
```

**filename: multiclip.py (Enhanced)**
```python
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
        self.orderly_active = False
        self.orderly_index = 1
        
        # Drag and drop state
        self.drag_source = None
        self.drag_data = None
        
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
        self.main_window.set_orderly_callback(self._on_orderly_action)
    
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
        if new_mode == "Orderly":
            self.orderly_active = True
            self.orderly_index = 1
            self.show_toast("Orderly Mode", "Sequential copying activated")
        else:
            self.orderly_active = False
            if new_mode != "Diff-Marker":  # Don't show toast for diff marker
                self.show_toast(f"{new_mode} Mode", f"{new_mode} mode activated")
    
    def _on_orderly_action(self, action: str):
        """Handle orderly mode actions"""
        if action == "toggle":
            self.orderly_active = not self.orderly_active
            if self.orderly_active:
                self.orderly_index = 1
                self.show_toast("Orderly Mode", "Sequential copying activated")
            else:
                self.show_toast("Orderly Mode", "Sequential copying deactivated")
            
            self.main_window.update_orderly_status(
                "Active" if self.orderly_active else "Inactive",
                self.orderly_active
            )
        elif action == "reset":
            self.orderly_index = 1
            self.show_toast("Orderly Mode", "Sequence reset to slot 1")
    
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
            
            if self.orderly_active:
                # Orderly mode: use sequential slot
                actual_slot = self.orderly_index - 1  # Convert to 0-based
                slot_key = f"slot_{self.orderly_index}"
                
                self.clipboard_slots[slot_key] = clipboard_content
                self.clipboard_manager.store_in_slot(actual_slot, clipboard_content)
                self.save_dictionary()
                
                # Update UI
                preview = clipboard_content[:50] + "..." if len(clipboard_content) > 50 else clipboard_content
                self.main_window.update_slot(actual_slot, clipboard_content, preview)
                
                self.show_toast("Orderly Copy", f"Slot {self.orderly_index} updated")
                
                # Move to next slot
                self.orderly_index += 1
                if self.orderly_index > 10:
                    self.orderly_index = 1
            else:
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
        self.show_toast("MultiClip Started", "System ready with Diff-Marker integration!")
        self.main_window.run()

if __name__ == "__main__":
    app = MultiClipSystem()
    app.run()
```