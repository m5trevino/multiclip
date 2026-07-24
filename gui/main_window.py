import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Callable, Optional, List
import json
import os

class EditOverlay:
    """A modal overlay for viewing and editing long snippets."""
    def __init__(self, parent, title: str, initial_content: str, on_save: Callable):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("600x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.on_save = on_save
        self.initial_content = initial_content
        
        self._create_widgets()
        
    def _create_widgets(self):
        self.text = tk.Text(self.window, font=('Consolas', 10), padx=10, pady=10, undo=True)
        self.text.pack(fill='both', expand=True)
        self.text.insert('1.0', self.initial_content)
        
        btn_frame = tk.Frame(self.window, bg='#333', pady=5)
        btn_frame.pack(fill='x')
        
        tk.Button(btn_frame, text="SAVE (Ctrl+S)", command=self.save, 
                  bg='gold', fg='black', font=('Arial', 8, 'bold')).pack(side='right', padx=10)
        tk.Button(btn_frame, text="CANCEL (Esc)", command=self.window.destroy,
                  bg='#555', fg='white', font=('Arial', 8)).pack(side='right')
        
        # Binds
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        self.text.bind('<Control-s>', lambda e: self.save())
        self.text.focus_set()

    def save(self):
        new_content = self.text.get('1.0', 'end-1c')
        self.on_save(new_content)
        self.window.destroy()

class ClipmanPreviewPopup:
    """Popup for viewing full text of clipman entries."""
    def __init__(self, parent, entries, start_index=0, transfer_callback=None):
        self.parent = parent
        self.entries = list(entries)
        self.current_idx = start_index
        self._bind_id = None
        self.transfer_callback = transfer_callback

        self.window = tk.Toplevel(parent)
        self.window.title("Clipman Preview")
        self.window.geometry("720x560")
        self.window.configure(bg="#2b2b2b")
        self.window.transient(parent)
        self.window.lift()

        self._create_widgets()
        self._bind_close()
        self._show_current()

    def _create_widgets(self):
        # Header bar
        header = tk.Frame(self.window, bg="#333")
        header.pack(fill='x', padx=0, pady=0)

        self.title_label = tk.Label(header, text="", font=('Arial', 11, 'bold'),
                                    fg='white', bg='#333')
        self.title_label.pack(side='left', padx=10, pady=8)

        tk.Button(header, text="✕", command=self.close,
                  bg='#c44', fg='white', font=('Arial', 10, 'bold'),
                  bd=0, padx=10, cursor='hand2').pack(side='right', padx=5, pady=5)

        # Mode toggle: Single vs Show All
        mode_frame = tk.Frame(header, bg='#333')
        mode_frame.pack(side='right', padx=10)

        self.mode_var = tk.StringVar(value="single")
        tk.Radiobutton(mode_frame, text="Single", variable=self.mode_var,
                       value="single", bg='#333', fg='white', selectcolor='#555',
                       activebackground='#333', activeforeground='white',
                       command=self._on_mode_change).pack(side='left')
        tk.Radiobutton(mode_frame, text="Show All", variable=self.mode_var,
                       value="all", bg='#333', fg='white', selectcolor='#555',
                       activebackground='#333', activeforeground='white',
                       command=self._on_mode_change).pack(side='left')

        # Navigation bar (single mode only)
        self.nav_frame = tk.Frame(self.window, bg="#2b2b2b")
        self.nav_frame.pack(fill='x', padx=10, pady=5)

        self.prev_btn = tk.Button(self.nav_frame, text="◀ Prev", command=self._prev,
                                  bg='#444', fg='white', font=('Arial', 9))
        self.prev_btn.pack(side='left')

        self.counter_label = tk.Label(self.nav_frame, text="", font=('Arial', 10),
                                      fg='#aaa', bg='#2b2b2b')
        self.counter_label.pack(side='left', padx=15)

        self.next_btn = tk.Button(self.nav_frame, text="Next ▶", command=self._next,
                                  bg='#444', fg='white', font=('Arial', 9))
        self.next_btn.pack(side='left')

        # Text area
        self.text = tk.Text(self.window, font=('Consolas', 10), wrap='word',
                            bg='#1e1e1e', fg='#e0e0e0', padx=10, pady=10)
        self.text.pack(fill='both', expand=True, padx=10, pady=(0, 5))
        self.text.config(state='disabled')

        # Transfer bar (slot spinbox + Transfer button)
        if self.transfer_callback:
            xfer_frame = tk.Frame(self.window, bg="#2b2b2b")
            xfer_frame.pack(fill='x', padx=10, pady=(0, 10))
            tk.Label(xfer_frame, text="Transfer to slot:", bg="#2b2b2b", fg="#aaa",
                     font=('Arial', 9)).pack(side='left')
            self.xfer_spin = tk.Spinbox(xfer_frame, from_=1, to=30, width=4,
                                        font=('Arial', 9, 'bold'))
            self.xfer_spin.pack(side='left', padx=(5, 5))
            tk.Button(xfer_frame, text="Transfer", command=self._do_transfer,
                      bg='#2a5a2a', fg='white', font=('Arial', 9, 'bold')).pack(side='left')

    def _do_transfer(self):
        if not self.transfer_callback:
            return
        try:
            slot = int(self.xfer_spin.get())
        except ValueError:
            return
        entry = self.entries[self.current_idx]
        content = entry.decoded_content if hasattr(entry, 'decoded_content') else str(entry)
        self.transfer_callback(slot, content)

    def _bind_close(self):
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.bind('<Escape>', lambda e: self.close())
        # Click outside to close: bind to parent; clicks inside popup don't propagate
        self._bind_id = self.parent.bind('<Button-1>', lambda e: self.close(), add='+')
        # Also close on focus out as a fallback
        self.window.bind('<FocusOut>', lambda e: self.window.after(100, self._check_focus))

    def _check_focus(self):
        if not self.window.winfo_exists():
            return
        try:
            if self.window.focus_displayof() != self.window:
                self.close()
        except:
            pass

    def _on_mode_change(self):
        if self.mode_var.get() == "all":
            self.nav_frame.pack_forget()
            self._show_all()
        else:
            self.nav_frame.pack(fill='x', padx=10, pady=5)
            self._show_current()

    def _show_current(self):
        if not self.entries:
            return
        entry = self.entries[self.current_idx]
        content = entry.decoded_content if hasattr(entry, 'decoded_content') else str(entry)

        self.text.config(state='normal')
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', content)
        self.text.config(state='disabled')

        self.title_label.config(text=f"Preview — Item {self.current_idx + 1} of {len(self.entries)}")
        self.counter_label.config(text=f"{self.current_idx + 1} / {len(self.entries)}")

        self.prev_btn.config(state='normal' if self.current_idx > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_idx < len(self.entries) - 1 else 'disabled')

    def _show_all(self):
        self.text.config(state='normal')
        self.text.delete('1.0', 'end')
        for i, entry in enumerate(self.entries):
            content = entry.decoded_content if hasattr(entry, 'decoded_content') else str(entry)
            self.text.insert('end', f"{'='*40}  Item {i+1}  {'='*40}\n\n")
            self.text.insert('end', content)
            self.text.insert('end', "\n\n")
        self.text.config(state='disabled')
        self.title_label.config(text=f"Preview — All {len(self.entries)} Items")

    def _prev(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            self._show_current()

    def _next(self):
        if self.current_idx < len(self.entries) - 1:
            self.current_idx += 1
            self._show_current()

    def close(self):
        try:
            if self._bind_id:
                self.parent.unbind('<Button-1>', self._bind_id)
        except:
            pass
        try:
            self.window.destroy()
        except:
            pass


class SlotDisplay(ttk.Frame):
    """
    High-density slot display.
    Includes: Slot ID, Order Number Field, and Text Preview.
    """
    def __init__(self, parent, slot_id: int, on_select: Callable, on_order_change: Callable, on_edit: Callable):
        super().__init__(parent)
        self.slot_id = slot_id
        self.on_select = on_select
        self.on_order_change = on_order_change
        self.on_edit = on_edit
        self.content = ""
        self.preview = ""
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Container for the row
        self.container = tk.Frame(self, bg='#f0f0f0', bd=1, relief='flat')
        self.container.pack(fill='x', padx=1, pady=1)

        # 1. Order Field (Numeric input)
        self.order_var = tk.StringVar(value=str(self.slot_id + 1))
        self.order_entry = tk.Entry(self.container, textvariable=self.order_var, 
                                   width=3, font=('Arial', 9, 'bold'), 
                                   justify='center', bd=1)
        self.order_entry.pack(side='left', padx=2)
        self.order_entry.bind('<FocusOut>', lambda e: self.on_order_change(self.slot_id, self.order_var.get()))

        # 2. Slot ID Label
        self.id_label = tk.Label(self.container, text=f"S{self.slot_id+1:02d}", 
                                font=('Consolas', 8), fg='#666', bg='#f0f0f0')
        self.id_label.pack(side='left', padx=2)

        # 3. Content Preview (Single line, very dense)
        self.preview_label = tk.Label(self.container, text="(empty)", 
                                     font=('Arial', 9), anchor='w', 
                                     bg='white', cursor='hand2',
                                     width=35, relief='flat', padx=5)
        self.preview_label.pack(side='left', fill='x', expand=True, padx=2)
        
        # Interaction: Left click to select, Right click to EDIT, Middle click to COPY
        self.preview_label.bind('<Button-1>', lambda e: self.on_select(self.slot_id))
        self.preview_label.bind('<Button-3>', lambda e: self.on_edit(self.slot_id))
        self.preview_label.bind('<Button-2>', lambda e: self._on_copy_slot())
        
        # 4. Char count / Status
        self.status_label = tk.Label(self.container, text="0", 
                                    font=('Arial', 7), fg='gray', bg='#f0f0f0', width=4)
        self.status_label.pack(side='right', padx=2)

    def _on_copy_slot(self):
        if self.content and hasattr(self.master, 'master'):
            # Walk up to find the MainWindow instance
            mw = self.master.master
            while mw and not hasattr(mw, 'copy_to_clipboard_callback'):
                mw = mw.master if hasattr(mw, 'master') else None
            if mw and mw.copy_to_clipboard_callback:
                mw.copy_to_clipboard_callback(self.content, f"Slot {self.slot_id+1}")

    def update_content(self, content: str, preview: str):
        self.content = content
        self.preview = preview
        
        clean_preview = preview.replace('\n', ' ').strip()
        if not clean_preview:
            clean_preview = "(empty)"
            
        self.preview_label.config(text=clean_preview[:50])
        
        if content:
            self.status_label.config(text=str(len(content)), fg='blue')
            self.preview_label.config(bg='#e8f4ff')
        else:
            self.status_label.config(text="0", fg='gray')
            self.preview_label.config(bg='white')
            
    def set_order(self, order_num: int):
        self.order_var.set(str(order_num))

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MultiClip V2 - Industrial Workstation")
        self.root.geometry("1100x850")
        self.root.configure(bg='#f5f5f5')
        
        # Callbacks
        self.slot_select_callback: Optional[Callable] = None
        self.mode_change_callback: Optional[Callable] = None
        self.orderly_callback: Optional[Callable] = None
        self.order_change_callback: Optional[Callable] = None
        self.normalize_callback: Optional[Callable] = None
        self.vault_save_callback: Optional[Callable] = None
        self.slot_edit_callback: Optional[Callable] = None
        self.vault_edit_callback: Optional[Callable] = None
        
        # V3 callbacks
        self.preview_transfer_callback: Optional[Callable] = None
        self.one_per_line_callback: Optional[Callable] = None
        self.send_to_snippet_callback: Optional[Callable] = None
        self.orderly_submode_callback: Optional[Callable] = None
        self.slot_click_callback: Optional[Callable] = None
        self.orderly_paste_callback: Optional[Callable] = None
        self.copy_to_clipboard_callback: Optional[Callable] = None
        
        self.slot_displays: Dict[int, SlotDisplay] = {}
        self.manual_start_slot: Optional[int] = None
        self.slot_mode_var = tk.StringVar(value="auto")
        self.orderly_submode = "fifo"
        self._flash_active: Dict[int, Any] = {}
        self.current_mode = "Multiclip"
        
        self.clipboard_manager = None
        self.history_panel = None
        
        self._create_ui()
    
    def set_clipboard_manager(self, clipboard_manager):
        self.clipboard_manager = clipboard_manager
        
    def set_history_parser(self, parser, on_deploy_callback):
        from gui.history_panel import HistoryPanel
        self.history_panel = HistoryPanel(self.right_panel, parser, on_deploy_callback)
        self.history_panel.pack(fill='both', expand=True)
        
    def _create_ui(self):
        # Ensure V3 state vars exist (for monkey-patched tests that skip __init__)
        if not hasattr(self, 'slot_mode_var'):
            self.slot_mode_var = tk.StringVar(value="auto")
        if not hasattr(self, 'manual_start_slot'):
            self.manual_start_slot = None
        if not hasattr(self, 'orderly_submode'):
            self.orderly_submode = "fifo"
        if not hasattr(self, '_flash_active'):
            self._flash_active = {}

        # --- Top Toolbar ---
        toolbar = tk.Frame(self.root, bg='#333', height=40)
        toolbar.pack(fill='x', side='top')
        
        title_label = tk.Label(toolbar, text="MULTICLIP V2", font=('Arial', 12, 'bold'), 
                              fg='white', bg='#333', padx=15)
        title_label.pack(side='left')
        
        # Mode Selection
        self.mode_var = tk.StringVar(value="Multiclip")
        self.mode_buttons: Dict[str, tk.Radiobutton] = {}
        for mode in ["Multiclip", "Orderly", "Vault", "Sequential"]:
            rb = tk.Radiobutton(toolbar, text=mode, variable=self.mode_var, value=mode,
                               command=self._on_mode_change, bg='#333', fg='white',
                               selectcolor='#555', activebackground='#444', 
                               activeforeground='gold', font=('Arial', 9))
            rb.pack(side='left', padx=10)
            self.mode_buttons[mode] = rb

        # Global Actions
        self.help_btn = tk.Button(toolbar, text="?", command=self._show_help,
                                 bg='#555', fg='white', font=('Arial', 8, 'bold'), bd=0, padx=10)
        self.help_btn.pack(side='right', padx=10, pady=5)

        self.norm_btn = tk.Button(toolbar, text="NORMALIZE SEQ", command=self._on_normalize,
                                 bg='#444', fg='gold', font=('Arial', 8, 'bold'), bd=0, padx=10)
        self.norm_btn.pack(side='right', padx=10, pady=5)
        
        self.clear_btn = tk.Button(toolbar, text="CLEAR ALL", command=self._clear_all_slots,
                                  bg='#444', fg='red', font=('Arial', 8, 'bold'), bd=0, padx=10)
        self.clear_btn.pack(side='right', padx=5, pady=5)

        # --- Main Layout ---
        main_container = tk.Frame(self.root, bg='#f5f5f5')
        main_container.pack(fill='both', expand=True, padx=5, pady=5)

        # LEFT COLUMN: Workbench (30 slots) + Snippets directly underneath it (bottom left)
        left_vbox = tk.Frame(main_container)
        left_vbox.pack(side='left', fill='both', expand=True)

        # 1. Left Panel (The 30-Slot Bench)
        self.left_panel = tk.LabelFrame(left_vbox, text=" WORK BENCH (30 SLOTS) ", 
                                       font=('Arial', 10, 'bold'), padx=5, pady=5)
        self.left_panel.pack(side='top', fill='both', expand=True)

        # Scrollable area for slots
        canvas_frame = tk.Frame(self.left_panel)
        canvas_frame.pack(fill='both', expand=True)
        
        self.slot_canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        self.slot_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.slot_canvas.yview)
        self.slot_canvas.configure(yscrollcommand=self.slot_scroll.set)
        
        self.slot_scroll.pack(side='right', fill='y')
        self.slot_canvas.pack(side='left', fill='both', expand=True)
        
        self.slots_inner = tk.Frame(self.slot_canvas)
        self.slot_canvas.create_window((0, 0), window=self.slots_inner, anchor='nw')

        # Vertical columns as requested:
        # Left column: 1 (top) → 15 (bottom)
        # Right column: 16 (top) → 30 (bottom)
        for i in range(15):
            # Left column (slots 1-15)
            slot = SlotDisplay(self.slots_inner, i, self._on_slot_select,
                               self._on_order_change, self._on_slot_edit)
            slot.grid(row=i, column=0, sticky='ew', padx=2, pady=1)
            self.slot_displays[i] = slot

        for i in range(15):
            # Right column (slots 16-30)
            slot_idx = 15 + i
            slot = SlotDisplay(self.slots_inner, slot_idx, self._on_slot_select,
                               self._on_order_change, self._on_slot_edit)
            slot.grid(row=i, column=1, sticky='ew', padx=2, pady=1)
            self.slot_displays[slot_idx] = slot

        # Make both columns expand evenly
        self.slots_inner.grid_columnconfigure(0, weight=1)
        self.slots_inner.grid_columnconfigure(1, weight=1)

        self.slots_inner.bind("<Configure>", lambda e: self.slot_canvas.configure(scrollregion=self.slot_canvas.bbox("all")))
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

        # 3. Snippets Panel — BOTTOM LEFT, directly under the 30 OG slots (as requested)
        self.snippets_panel = tk.LabelFrame(left_vbox, text=" SNIPPETS (persistent) ", 
                                            font=('Arial', 10, 'bold'), padx=5, pady=5)
        self.snippets_panel.pack(side='bottom', fill='x', padx=2, pady=(6, 0))

        self.snippet_entries: Dict[int, tk.Entry] = {}
        for i in range(8):  # 8 quick snippets
            row = tk.Frame(self.snippets_panel)
            row.pack(fill='x', pady=1)

            tk.Label(row, text=f"S{i+1}:", font=('Consolas', 8, 'bold'), width=3).pack(side='left')

            entry = tk.Entry(row, font=('Arial', 9), bd=1)
            entry.pack(side='left', fill='x', expand=True, padx=2)
            self.snippet_entries[i] = entry

            save_btn = tk.Button(row, text="Save", font=('Arial', 7), command=lambda idx=i: self._save_snippet(idx))
            save_btn.pack(side='right', padx=2)

            copy_btn = tk.Button(row, text="📋", font=('Arial', 7),
                                 command=lambda idx=i: self._copy_snippet(idx))
            copy_btn.pack(side='right', padx=2)

            x_btn = tk.Button(row, text="X", font=('Arial', 7), fg='red',
                              command=lambda idx=i: self._remove_snippet(idx))
            x_btn.pack(side='right', padx=2)

        self.snippets_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "snippets.json")
        self._load_snippets()

        # 2. Right Panel (Clipman History + Vault)
        self.right_panel = tk.Frame(main_container)
        self.right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Vault Panel (kept for now)
        self.vault_panel = tk.LabelFrame(self.right_panel, text=" SNIPPET VAULT ", 
                                        font=('Arial', 10, 'bold'), padx=5, pady=5)
        
        self.vault_inner = tk.Frame(self.vault_panel)
        self.vault_inner.pack(fill='both', expand=True)
        
        self.vault_entries: Dict[int, tk.Entry] = {}
        for i in range(10): # First 10 get hotkeys
            row = tk.Frame(self.vault_inner)
            row.pack(fill='x', pady=1)
            
            tk.Label(row, text=f"V{i+1}:", font=('Consolas', 8, 'bold'), width=4).pack(side='left')
            
            entry = tk.Entry(row, font=('Arial', 9), bd=1)
            entry.pack(side='left', fill='x', expand=True, padx=2)
            self.vault_entries[i] = entry
            
            # Save button for each
            btn = tk.Button(row, text="💾", font=('Arial', 7), command=lambda idx=i: self._on_vault_save(idx),
                           bg='#eee', bd=1)
            btn.pack(side='right')
            
            # EDIT button for each
            edit_btn = tk.Button(row, text="✎", font=('Arial', 7), command=lambda idx=i: self._on_vault_edit(idx),
                                bg='#eee', bd=1)
            edit_btn.pack(side='right', padx=2)

        # --- NEW: Clipman History Panel (added for your vision) ---
        self.clipman_panel = tk.LabelFrame(self.right_panel, text=" CLIPMAN HISTORY ", 
                                           font=('Arial', 10, 'bold'), padx=5, pady=5)
        self.clipman_panel.pack(fill='both', expand=True, pady=(10, 0))

        # --- Action buttons at TOP of Clipman panel ---
        btn_frame = tk.Frame(self.clipman_panel)
        btn_frame.pack(fill='x', pady=(0, 3))

        lock_btn = tk.Button(btn_frame, text="LOCK SELECTION",
                             command=self._on_clipman_lock,
                             bg='#555', fg='white', font=('Arial', 9, 'bold'))
        lock_btn.pack(side='left', expand=True, fill='x', padx=(0, 2))

        batch_btn = tk.Button(btn_frame, text="Block Bundle",
                              command=self._on_clipman_transfer_batch,
                              bg='#333', fg='#aaffaa', font=('Arial', 9, 'bold'))
        batch_btn.pack(side='left', expand=True, fill='x', padx=(2, 0))

        send_snip_btn = tk.Button(btn_frame, text="Send to Snippet",
                                  command=self._on_send_to_snippet,
                                  bg='#2a5a2a', fg='#aaffaa', font=('Arial', 8, 'bold'))
        send_snip_btn.pack(side='left', expand=True, fill='x', padx=(2, 0))

        # Copy Selected from history
        copy_hist_btn = tk.Button(btn_frame, text="📋 Copy",
                                  command=self._on_copy_history_selected,
                                  bg='#664400', fg='#ffdd88', font=('Arial', 8, 'bold'))
        copy_hist_btn.pack(side='left', expand=True, fill='x', padx=(2, 0))

        one_slot_frame = tk.Frame(self.clipman_panel)
        one_slot_frame.pack(fill='x', pady=(0, 3))

        one_slot_btn = tk.Button(one_slot_frame, text="1 slot per line",
                                 command=self._on_transfer_one_slot_per_line,
                                 bg='#444', fg='#ffcc66', font=('Arial', 8, 'bold'))
        one_slot_btn.pack(fill='x', expand=True, side='left')

        # Mode toggle: Auto-Sequential vs Manual
        mode_toggle = tk.Frame(one_slot_frame, bg='#444')
        mode_toggle.pack(side='right', padx=(4, 0))
        tk.Radiobutton(mode_toggle, text="Auto", variable=self.slot_mode_var,
                       value="auto", bg='#444', fg='white', selectcolor='#555',
                       font=('Arial', 7)).pack(side='left')
        tk.Radiobutton(mode_toggle, text="Manual", variable=self.slot_mode_var,
                       value="manual", bg='#444', fg='white', selectcolor='#555',
                       font=('Arial', 7)).pack(side='left')

        clipman_inner = tk.Frame(self.clipman_panel)
        clipman_inner.pack(fill='both', expand=True)

        # Scrollable list for Clipman entries
        self.clipman_listbox = tk.Listbox(clipman_inner, selectmode='extended', 
                                          font=('Consolas', 9), height=12)
        clipman_scroll = ttk.Scrollbar(clipman_inner, orient='vertical', 
                                       command=self.clipman_listbox.yview)
        self.clipman_listbox.configure(yscrollcommand=clipman_scroll.set)

        self.clipman_listbox.pack(side='left', fill='both', expand=True)
        clipman_scroll.pack(side='right', fill='y')

        # Pagination controls
        self.clipman_page_frame = tk.Frame(self.clipman_panel, bg='#eee')
        self.clipman_page_frame.pack(fill='x', pady=(3, 0))

        self.clipman_prev_btn = tk.Button(self.clipman_page_frame, text="◀ Prev",
                                          command=self._clipman_prev_page,
                                          bg='#555', fg='white', font=('Arial', 8))
        self.clipman_prev_btn.pack(side='left', padx=(0, 5))

        self.clipman_page_label = tk.Label(self.clipman_page_frame, text="Page 1/1",
                                           font=('Arial', 9, 'bold'), bg='#eee')
        self.clipman_page_label.pack(side='left', padx=5)

        self.clipman_next_btn = tk.Button(self.clipman_page_frame, text="Next ▶",
                                          command=self._clipman_next_page,
                                          bg='#555', fg='white', font=('Arial', 8))
        self.clipman_next_btn.pack(side='left', padx=(5, 0))

        # Orderly subframe (hidden by default, shown in Orderly mode)
        self.orderly_subframe = tk.Frame(self.right_panel, bg='#eee')
        self.orderly_subframe.pack(fill='x', pady=(6, 0))
        self.orderly_subframe.pack_forget()  # hidden initially

        fifo_lifo_frame = tk.Frame(self.orderly_subframe, bg='#eee')
        fifo_lifo_frame.pack(fill='x', pady=2)

        # FIFO/LIFO share the same distinctive color so they read as one group
        self.fifo_btn = tk.Button(fifo_lifo_frame, text="FIFO",
                                  command=lambda: self._set_orderly_submode("fifo"),
                                  bg='#0066aa', fg='white', font=('Arial', 8, 'bold'))
        self.fifo_btn.pack(side='left', expand=True, fill='x', padx=(0, 2))

        self.lifo_btn = tk.Button(fifo_lifo_frame, text="LIFO",
                                  command=lambda: self._set_orderly_submode("lifo"),
                                  bg='#0066aa', fg='white', font=('Arial', 8, 'bold'))
        self.lifo_btn.pack(side='left', expand=True, fill='x', padx=(2, 0))

        self.paste_next_btn = tk.Button(self.orderly_subframe, text="Paste Next",
                                        command=self._on_paste_next,
                                        bg='#2a5a2a', fg='white', font=('Arial', 9, 'bold'))
        self.paste_next_btn.pack(fill='x', pady=(2, 0))

        # Double-click to preview full text
        self.clipman_listbox.bind('<Double-Button-1>', self._on_clipman_double_click)

        # --- Bottom Status ---
        self.status_bar = tk.Frame(self.root, bg='#ddd', height=25)
        self.status_bar.pack(fill='x', side='bottom')
        
        self.bottom_status = tk.Label(self.status_bar, text="Ready | Target: Any", 
                                     bg='#ddd', font=('Arial', 8), anchor='w', padx=10)
        self.bottom_status.pack(side='left')
        
        self.pos_status = tk.Label(self.status_bar, text="Seq: 1/30", 
                                  bg='#ddd', font=('Arial', 8, 'bold'), anchor='e', padx=10)
        self.pos_status.pack(side='right')

        # Show initial panel
        self._show_mode_panel("Multiclip")

        # Clipman data + callback
        self.clipman_entries: list = []
        self.clipman_transfer_callback: Optional[Callable] = None
        self.locked_groups: list = []  # list of lists of selected indices

    def _on_slot_edit(self, slot_id: int):
        if self.slot_edit_callback:
            content = self.slot_displays[slot_id].content
            EditOverlay(self.root, f"Edit Slot {slot_id+1}", content, 
                        lambda new_c: self.slot_edit_callback(slot_id, new_c))

    def _on_vault_edit(self, index: int):
        if self.vault_edit_callback:
            content = self.vault_entries[index].get()
            EditOverlay(self.root, f"Edit Vault V{index+1}", content, 
                        lambda new_c: self.vault_edit_callback(index, new_c))

    def _on_vault_save(self, index: int):
        if self.vault_save_callback:
            content = self.vault_entries[index].get()
            self.vault_save_callback(index, content)

    def update_vault_item(self, index: int, content: str):
        if index in self.vault_entries:
            self.vault_entries[index].delete(0, 'end')
            self.vault_entries[index].insert(0, content)

    # ---------------- Clipman History support (new for your vision) ----------------
    def set_clipman_entries(self, entries: list):
        """Store all entries and display paginated view (50 per page).
        Supports unlimited history - only renders current page to UI."""
        self.clipman_all_entries = list(entries)
        self.clipman_current_page = 0
        self.clipman_page_size = 50
        self._update_clipman_page_display()
        # Update count label to show total
        total = len(self.clipman_all_entries)
        if hasattr(self, 'count_label'):
            self.count_label.configure(text=f"{total} entries")

    def _update_clipman_page_display(self):
        """Render only the current page into the listbox."""
        self.clipman_listbox.delete(0, tk.END)
        start = self.clipman_current_page * self.clipman_page_size
        end = start + self.clipman_page_size
        page_entries = self.clipman_all_entries[start:end]
        for e in page_entries:
            preview = e.preview if hasattr(e, 'preview') else str(e)[:80]
            self.clipman_listbox.insert(tk.END, preview)

        total_pages = max(1, (len(self.clipman_all_entries) + self.clipman_page_size - 1) // self.clipman_page_size)
        self.clipman_page_label.config(text=f"Page {self.clipman_current_page + 1}/{total_pages}")

        self.clipman_prev_btn.config(state='normal' if self.clipman_current_page > 0 else 'disabled')
        self.clipman_next_btn.config(state='normal' if self.clipman_current_page < total_pages - 1 else 'disabled')

    def _clipman_prev_page(self):
        if self.clipman_current_page > 0:
            self.clipman_current_page -= 1
            self._update_clipman_page_display()

    def _clipman_next_page(self):
        total_pages = max(1, (len(self.clipman_all_entries) + self.clipman_page_size - 1) // self.clipman_page_size)
        if self.clipman_current_page < total_pages - 1:
            self.clipman_current_page += 1
            self._update_clipman_page_display()

    def _get_clipman_selected_full_indices(self):
        """Map listbox selection indices to full entry list indices."""
        listbox_indices = self.clipman_listbox.curselection()
        start = self.clipman_current_page * self.clipman_page_size
        return [start + i for i in listbox_indices]

    def _on_clipman_double_click(self, event=None):
        """Double-click: show preview popup for selected entries."""
        full_indices = self._get_clipman_selected_full_indices()
        if not full_indices:
            return
        selected_entries = [self.clipman_all_entries[i] for i in full_indices]
        ClipmanPreviewPopup(self.root, selected_entries, transfer_callback=self.preview_transfer_callback)

    def set_clipman_transfer_callback(self, callback: Callable):
        self.clipman_transfer_callback = callback

    def start_live_clipman_refresh(self, parser, interval_ms: int = 3000):
        """Poll the clipman textsrc file for changes and auto-refresh the listbox."""
        self._clipman_parser = parser
        self._clipman_interval = interval_ms
        self._clipman_last_mtime = 0
        self._poll_clipman()

    def _poll_clipman(self):
        try:
            filepath = getattr(self._clipman_parser, 'filepath', None)
            if filepath and os.path.exists(filepath):
                mtime = os.path.getmtime(filepath)
                if mtime != self._clipman_last_mtime:
                    self._clipman_last_mtime = mtime
                    total = getattr(self._clipman_parser, 'get_total_count', lambda: 0)()
                    entries = self._clipman_parser.parse(max_entries=total)
                    self.set_clipman_entries(entries)
                    print(f"[CLIPMAN] Auto-refreshed: {len(entries)} entries")
        except Exception as e:
            print(f"[CLIPMAN POLL] {e}")
        # Schedule next poll
        self.root.after(self._clipman_interval, self._poll_clipman)

    def _on_clipman_lock(self):
        full_indices = self._get_clipman_selected_full_indices()
        if not full_indices:
            return
        self.locked_groups.append(full_indices)
        # Visual feedback - mark locked items on current page
        start = self.clipman_current_page * self.clipman_page_size
        for idx in full_indices:
            if start <= idx < start + self.clipman_page_size:
                lb_idx = idx - start
                current_text = self.clipman_listbox.get(lb_idx)
                if not current_text.startswith("[LOCKED]"):
                    self.clipman_listbox.delete(lb_idx)
                    self.clipman_listbox.insert(lb_idx, "[LOCKED] " + current_text)

    def _get_all_selected_entries(self):
        """Collect entries from locked groups + current selection."""
        all_indices = set()
        for group in self.locked_groups:
            all_indices.update(group)
        all_indices.update(self._get_clipman_selected_full_indices())
        return [self.clipman_all_entries[i] for i in sorted(all_indices) if i < len(self.clipman_all_entries)]

    def _on_clipman_transfer_batch(self):
        if not self.clipman_transfer_callback:
            return
        all_to_transfer = self._get_all_selected_entries()
        if all_to_transfer:
            # Block Bundle: concatenate all selections into one slot
            parts = []
            for item in all_to_transfer:
                if hasattr(item, 'decoded_content'):
                    parts.append(item.decoded_content)
                else:
                    parts.append(str(item))
            bundle = "\n".join(parts)
            self.clipman_transfer_callback([bundle])
        self.locked_groups = []
        self._update_clipman_page_display()

    def _on_transfer_one_slot_per_line(self):
        """Transfer selected entries, one per slot (sequential with wrap)."""
        if not self.one_per_line_callback:
            return
        all_items = self._get_all_selected_entries()
        if not all_items:
            return
        start_slot = self.manual_start_slot if (self.slot_mode_var.get() == "manual" and self.manual_start_slot) else 1
        self.one_per_line_callback(all_items, start_slot)
        self.locked_groups = []
        self._update_clipman_page_display()

    # ---------------- Snippets bottom-left persistence (add/save/replace survives restart) ----------------
    def _load_snippets(self):
        if not hasattr(self, 'snippets_file') or not self.snippets_file:
            return
        try:
            if os.path.exists(self.snippets_file):
                with open(self.snippets_file, 'r') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        idx = int(k)
                        if idx in self.snippet_entries:
                            self.snippet_entries[idx].delete(0, 'end')
                            self.snippet_entries[idx].insert(0, v)
        except Exception:
            pass  # silent, non-fatal

    def _save_snippet(self, idx: int):
        if idx not in self.snippet_entries:
            return
        content = self.snippet_entries[idx].get()
        try:
            data = {}
            if os.path.exists(self.snippets_file):
                with open(self.snippets_file, 'r') as f:
                    data = json.load(f)
            data[str(idx)] = content
            with open(self.snippets_file, 'w') as f:
                json.dump(data, f, indent=2)
            self._toast(f"Snippet S{idx+1} saved")
        except Exception as e:
            messagebox.showwarning("Snippets", f"Could not save: {e}")

    def _remove_snippet(self, idx: int):
        if idx not in self.snippet_entries:
            return
        self.snippet_entries[idx].delete(0, 'end')
        try:
            data = {}
            if os.path.exists(self.snippets_file):
                with open(self.snippets_file, 'r') as f:
                    data = json.load(f)
            data[str(idx)] = ""
            with open(self.snippets_file, 'w') as f:
                json.dump(data, f, indent=2)
            self._toast(f"Snippet S{idx+1} removed")
        except Exception as e:
            messagebox.showwarning("Snippets", f"Could not remove: {e}")

    def _copy_snippet(self, idx: int):
        if idx not in self.snippet_entries:
            return
        content = self.snippet_entries[idx].get()
        if content and self.copy_to_clipboard_callback:
            self.copy_to_clipboard_callback(content, f"Snippet S{idx+1}")

    def _on_copy_history_selected(self):
        all_items = self._get_all_selected_entries()
        if not all_items:
            return
        # Copy the first selected item (most common use case)
        item = all_items[0]
        content = item.decoded_content if hasattr(item, 'decoded_content') else str(item)
        if content and self.copy_to_clipboard_callback:
            self.copy_to_clipboard_callback(content, "History")
        self.locked_groups = []
        self._update_clipman_page_display()

    def set_copy_to_clipboard_callback(self, callback: Callable):
        self.copy_to_clipboard_callback = callback

    def _toast(self, msg: str):
        # lightweight status feedback
        try:
            self.bottom_status.config(text=msg)
            self.root.after(1800, lambda: self.bottom_status.config(text="Ready | Target: Any"))
        except:
            print(msg)

    def _show_mode_panel(self, mode: str):
        # Safe no-op (old UI had mode switching that is not present in this dense build)
        try:
            self.vault_panel.pack_forget()
        except:
            pass

    def _on_send_to_snippet(self):
        if not self.send_to_snippet_callback:
            return
        all_items = self._get_all_selected_entries()
        if not all_items:
            return
        contents = []
        for item in all_items:
            if hasattr(item, 'decoded_content'):
                contents.append(item.decoded_content)
            else:
                contents.append(str(item))
        self.send_to_snippet_callback(contents)
        self.locked_groups = []
        self._update_clipman_page_display()

    def _on_paste_next(self):
        if self.orderly_paste_callback:
            self.orderly_paste_callback()

    def _set_orderly_submode(self, mode: str):
        self.orderly_submode = mode
        # Visual feedback: active submode button gets highlighted
        if mode == "fifo":
            self.fifo_btn.config(bg='#0088dd')
            self.lifo_btn.config(bg='#0066aa')
        else:
            self.fifo_btn.config(bg='#0066aa')
            self.lifo_btn.config(bg='#0088dd')
        if self.orderly_submode_callback:
            self.orderly_submode_callback(mode)

    def set_preview_transfer_callback(self, callback: Callable):
        self.preview_transfer_callback = callback

    def set_one_per_line_callback(self, callback: Callable):
        self.one_per_line_callback = callback

    def set_send_to_snippet_callback(self, callback: Callable):
        self.send_to_snippet_callback = callback

    def set_orderly_submode_callback(self, callback: Callable):
        self.orderly_submode_callback = callback

    def set_slot_click_callback(self, callback: Callable):
        self.slot_click_callback = callback

    def set_orderly_paste_callback(self, callback: Callable):
        self.orderly_paste_callback = callback

    def flash_slot(self, slot_id, duration_ms=2000, color="#ffd700"):
        if slot_id not in self.slot_displays:
            return
        sd = self.slot_displays[slot_id]
        orig_bg = '#f0f0f0'
        if slot_id in self._flash_active:
            try:
                self.root.after_cancel(self._flash_active[slot_id]['timer'])
            except:
                pass
        steps = duration_ms // 200
        def _pulse(step=0):
            if step >= steps:
                sd.container.config(bg=orig_bg)
                self._flash_active.pop(slot_id, None)
                return
            new_bg = color if step % 2 == 0 else orig_bg
            sd.container.config(bg=new_bg)
            self._flash_active[slot_id] = {'timer': self.root.after(200, lambda: _pulse(step+1))}
        _pulse()

    def flash_snippet(self, idx, color="#32cd32", duration_ms=2000):
        if idx not in self.snippet_entries:
            return
        entry = self.snippet_entries[idx]
        orig_bg = entry.cget('bg') or 'white'
        if idx in self._flash_active:
            try:
                self.root.after_cancel(self._flash_active[idx]['timer'])
            except:
                pass
        steps = duration_ms // 200
        def _pulse(step=0):
            if step >= steps:
                entry.config(bg=orig_bg)
                self._flash_active.pop(idx, None)
                return
            new_bg = color if step % 2 == 0 else orig_bg
            entry.config(bg=new_bg)
            self._flash_active[idx] = {'timer': self.root.after(200, lambda: _pulse(step+1))}
        _pulse()

    def highlight_slot(self, slot_id, color):
        if slot_id in self.slot_displays:
            sd = self.slot_displays[slot_id]
            sd.container.config(bg=color, bd=2, relief='solid')

    def clear_slot_highlight(self, slot_id):
        if slot_id in self.slot_displays:
            sd = self.slot_displays[slot_id]
            sd.container.config(bg='#f0f0f0', bd=1, relief='flat')

    def show_orderly_status(self, queue_len, next_slot):
        self.update_bottom_status(f"Queue: {queue_len} items | Next: Slot {next_slot:02d}")

    def _on_mousewheel(self, event):
        self.slot_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_mode_change(self):
        new_mode = self.mode_var.get()
        if self.mode_change_callback:
            self.mode_change_callback(new_mode)
        # Update mode button colors: Orderly gets a unique standout color
        for mode, btn in self.mode_buttons.items():
            if mode == new_mode:
                if mode == "Orderly":
                    btn.config(fg='#ff6600', font=('Arial', 9, 'bold'))  # bright orange
                else:
                    btn.config(fg='gold', font=('Arial', 9, 'bold'))
            else:
                btn.config(fg='white', font=('Arial', 9))
        # Show/hide orderly subframe
        if new_mode == "Orderly":
            try:
                self.orderly_subframe.pack(fill='x', pady=(6, 0))
            except:
                pass
        else:
            try:
                self.orderly_subframe.pack_forget()
            except:
                pass
            
    def _on_slot_select(self, slot_id: int):
        if self.slot_mode_var.get() == "manual":
            self.manual_start_slot = slot_id + 1  # convert to 1-based
            # Brief gold highlight for feedback
            self.highlight_slot(slot_id, "#ffd700")
        if self.slot_select_callback:
            self.slot_select_callback(slot_id)
        if self.slot_click_callback:
            self.slot_click_callback(slot_id)
            
    def _on_order_change(self, slot_id: int, new_val: str):
        if self.order_change_callback:
            try:
                order_num = int(new_val)
                self.order_change_callback(slot_id, order_num)
            except ValueError:
                pass

    def _on_normalize(self):
        if self.normalize_callback:
            self.normalize_callback()

    def _show_help(self):
        help_text = """MultiClip V2 - Industrial Workstation Controls:

[PASTING]
Win + V      : Sequential Paste (Terminal-aware)
Win+Shift+V  : Batch Dump (All 30 slots)

[COPYING]
Win + 1-0    : Copy to Slots 1-10
Win+Alt+1-0  : Vault Snippet Paste

[ACTIONS]
Win + O      : Toggle Orderly Mode (Auto-fill Slots)
Right Click  : Edit Slot / Snippet content
Ctrl+S       : Save in Editor
Esc          : Cancel Edit
"""
        messagebox.showinfo("Command Manual", help_text)

    def _clear_all_slots(self):
        if messagebox.askyesno("Confirm", "Wipe all 30 slots? (Order will remain)"):
            if self.clipboard_manager:
                self.clipboard_manager.clear_all_slots()
                for slot in self.slot_displays.values():
                    slot.update_content("", "")

    # Public Updates
    def update_slot(self, slot_id: int, content: str, preview: str):
        if slot_id in self.slot_displays:
            self.slot_displays[slot_id].update_content(content, preview)
            
    def update_slot_order(self, slot_id: int, order_num: int):
        if slot_id in self.slot_displays:
            self.slot_displays[slot_id].set_order(order_num)

    def update_bottom_status(self, text: str):
        self.bottom_status.config(text=text)
        
    def update_seq_progress(self, current: int, total: int):
        self.pos_status.config(text=f"Seq: {current}/{total}")

    def run(self):
        self.root.mainloop()

    # ---------------- TOAST NOTIFICATIONS (with logo, detailed hotkey actions) ----------------
    def show_toast(self, action: str, slot: int = None, preview: str = "", duration: int = 2300):
        """Industrial style toast with logo and rich detail about the hotkey action."""
        try:
            toast = tk.Toplevel(self.root)
            toast.overrideredirect(True)
            toast.attributes("-topmost", True)
            toast.configure(bg="#1a1a1a", bd=2, relief="solid")

            # Position bottom-right of screen
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            w, h = 420, 92
            x = sw - w - 20
            y = sh - h - 60
            toast.geometry(f"{w}x{h}+{x}+{y}")

            # Logo
            logo_frame = tk.Frame(toast, bg="#1a1a1a")
            logo_frame.pack(side="left", padx=8, pady=6)

            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "chargers.png")
            if os.path.exists(logo_path):
                try:
                    img = tk.PhotoImage(file=logo_path)
                    # Scale down if too big
                    img = img.subsample(3, 3) if img.width() > 90 else img
                    logo_label = tk.Label(logo_frame, image=img, bg="#1a1a1a")
                    logo_label.image = img  # keep reference
                    logo_label.pack()
                except Exception:
                    tk.Label(logo_frame, text="MC", font=("Arial", 18, "bold"), fg="#ffcc00", bg="#1a1a1a").pack()
            else:
                tk.Label(logo_frame, text="MC", font=("Arial", 18, "bold"), fg="#ffcc00", bg="#1a1a1a").pack()

            # Text content
            text_frame = tk.Frame(toast, bg="#1a1a1a")
            text_frame.pack(side="left", fill="both", expand=True, padx=(4, 10), pady=6)

            # Main action line - detailed hotkey info
            if slot is not None:
                main_text = f"{action}  →  SLOT {slot:02d}"
            else:
                main_text = action

            title_label = tk.Label(text_frame, text=main_text,
                                   font=("Consolas", 11, "bold"), fg="#ffcc00", bg="#1a1a1a",
                                   anchor="w")
            title_label.pack(fill="x")

            # Preview / detail line
            if preview:
                clean = preview.replace("\n", " ")[:75]
                if len(preview) > 75:
                    clean += "..."
                detail = tk.Label(text_frame, text=clean,
                                  font=("Arial", 9), fg="#cccccc", bg="#1a1a1a",
                                  anchor="w", wraplength=300)
                detail.pack(fill="x", pady=(2, 0))

            # Small footer
            footer = tk.Label(text_frame, text="MULTICLIP V2 • INDUSTRIAL",
                              font=("Arial", 7), fg="#555555", bg="#1a1a1a", anchor="w")
            footer.pack(fill="x", pady=(4, 0))

            # Auto destroy
            toast.after(duration, lambda: toast.destroy() if toast.winfo_exists() else None)

            # Click to dismiss early
            toast.bind("<Button-1>", lambda e: toast.destroy())

        except Exception as e:
            print(f"[TOAST ERROR] {e}")
