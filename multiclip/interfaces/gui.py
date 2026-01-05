import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import pyperclip
import keyboard
from multiclip.core import MultiClipCore
from multiclip.shared.notify import toast
from multiclip.modules.importer import ClipImporter
from multiclip.modules.snippets import SnippetManager
from multiclip.interfaces.hud import HudWindow
from pathlib import Path
import threading

class MultiClipGUI:
    def __init__(self):
        self.core = MultiClipCore()
        self.snippets = SnippetManager()
        self.root = tk.Tk()
        self.root.title("MultiClip 2.2 - The Arsenal")
        
        icon_path = Path(__file__).parent.parent.parent / "assets/icons/multiclip.png"
        if icon_path.exists():
            self.root.iconphoto(True, tk.PhotoImage(file=icon_path))

        self.hud = None 
        self.build_ui()
        self.refresh_slots()
        
        # Start the heavy keyboard hooks
        self._start_hotkeys()

    # --- HOTKEYS (THE ROOT LOGIC) ---
    def _start_hotkeys(self):
        # Clean slate
        try: keyboard.unhook_all()
        except: pass

        # Classic 1-10
        for i in range(1, 11):
            key = str(i) if i < 10 else '0'
            # suppress=True stops the key from reaching the OS (prevents typing '!')
            keyboard.add_hotkey(f'ctrl+shift+{key}', lambda s=i: self.on_copy(s), suppress=True)
            keyboard.add_hotkey(f'ctrl+alt+{key}', lambda s=i: self.on_paste(s), suppress=True)

        # Sequential Master Keys
        keyboard.add_hotkey('ctrl+shift+space', self.on_seq_copy, suppress=True)
        keyboard.add_hotkey('ctrl+alt+space', self.on_seq_paste, suppress=True)
        
        # SMART INGEST (Ctrl+Shift+L)
        keyboard.add_hotkey('ctrl+shift+l', self.smart_ingest_clipboard, suppress=True)

    # --- ACTIONS ---
    def on_copy(self, slot):
        if self.mode_var.get() == "classic":
            # Threading ensures GUI doesn't freeze while xdotool runs
            threading.Thread(target=self._copy_thread, args=(slot,)).start()

    def _copy_thread(self, slot):
        self.core.copy_to_slot(slot)
        self.root.after(0, self.refresh_ui)
        self.root.after(0, lambda: toast("Locked", f"Slot {slot}"))

    def on_paste(self, slot):
        if self.mode_var.get() == "classic":
            threading.Thread(target=self._paste_thread, args=(slot,)).start()

    def _paste_thread(self, slot):
        self.core.paste_from_slot(slot)
        self.root.after(0, lambda: toast("Sent", f"Slot {slot}"))

    def on_seq_copy(self):
        if self.mode_var.get() == "sequential":
            threading.Thread(target=self._seq_copy_thread).start()

    def _seq_copy_thread(self):
        slot, _ = self.core.sequential_copy()
        self.root.after(0, self.refresh_ui)
        self.root.after(0, lambda: toast("Seq Copy", f"Saved Slot {slot}"))

    def on_seq_paste(self):
        if self.mode_var.get() == "sequential":
            threading.Thread(target=self._seq_paste_thread).start()

    def _seq_paste_thread(self):
        slot = self.core.sequential_paste()
        self.root.after(0, self.refresh_ui)
        self.root.after(0, lambda: toast("Seq Paste", f"Pasted Slot {slot}"))

    def smart_ingest_clipboard(self):
        # This one is fast, can run on main thread or simple thread
        threading.Thread(target=self._ingest_thread).start()

    def _ingest_thread(self):
        content = pyperclip.paste()
        if not content: return
        
        items = ClipImporter.smart_parse(content)
        if items:
            for i, text in enumerate(items):
                self.core.slots[i+1] = text
            self.core._save_slots()
            self.core.current_seq_slot = 1
            
            self.root.after(0, lambda: self.mode_var.set("sequential"))
            self.root.after(0, self.refresh_ui)
            # Check HUD in thread-safe way
            self.root.after(0, self._check_toggle_hud)
            
            self.root.after(0, lambda: toast("Smart Ingest", f"Parsed {len(items)} items"))

    def _check_toggle_hud(self):
        if not self.hud: self.toggle_hud()

    # --- UI BUILDER ---
    def build_ui(self):
        # MENUBAR
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Snippets Menu
        self.snip_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Snippets / Stash", menu=self.snip_menu)
        self.refresh_snippets_menu()

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Manual Data Import", command=self.open_manual_import)
        
        # Main Controls
        ctrl_frame = tk.Frame(self.root); ctrl_frame.pack(pady=5, fill="x", padx=10)
        
        tk.Label(ctrl_frame, text="Mode:").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="classic")
        tk.Radiobutton(ctrl_frame, text="Classic", variable=self.mode_var, value="classic").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(ctrl_frame, text="Sequential", variable=self.mode_var, value="sequential").pack(side=tk.LEFT, padx=5)
        
        tk.Button(ctrl_frame, text="HUD", command=self.toggle_hud, bg="#222", fg="white").pack(side=tk.RIGHT)

        # Treeview
        cols = ("Slot", "Preview")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", height=10)
        self.tree.heading("Slot", text="Slot"); self.tree.heading("Preview", text="Preview")
        self.tree.column("Slot", width=50, anchor="center"); self.tree.column("Preview", width=550)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Right Click Menu for Slots
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Add to Snippets", command=self.save_slot_to_snippets)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Bottom
        btn_frame = tk.Frame(self.root); btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT)

    # --- SNIPPETS LOGIC ---
    def refresh_snippets_menu(self):
        self.snip_menu.delete(0, tk.END)
        self.snip_menu.add_command(label="+ Add New Snippet", command=self.add_manual_snippet)
        self.snip_menu.add_separator()
        for label, content in self.snippets.snippets.items():
            # Click to copy to clipboard
            self.snip_menu.add_command(label=label, command=lambda c=content, l=label: self.use_snippet(c, l))

    def use_snippet(self, content, label):
        pyperclip.copy(content)
        toast("Snippet Copied", f"Loaded: {label}")

    def add_manual_snippet(self):
        key = simpledialog.askstring("New Snippet", "Name:")
        val = simpledialog.askstring("New Snippet", "Content:")
        if key and val:
            self.snippets.add(key, val)
            self.refresh_snippets_menu()

    def save_slot_to_snippets(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])
        slot_str = item['values'][0].replace(" ▶", "")
        real_text = self.core.slots.get(int(slot_str), "")
        
        key = simpledialog.askstring("Stash It", "Snippet Name:")
        if key:
            self.snippets.add(key, real_text)
            self.refresh_snippets_menu()
            toast("Stashed", f"Saved to snippets")

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    # --- MANUAL IMPORT WINDOW ---
    def open_manual_import(self):
        win = tk.Toplevel(self.root)
        win.title("Raw Data Ingest")
        win.geometry("400x300")
        
        tk.Label(win, text="Paste Data Here:").pack()
        txt = tk.Text(win, height=10); txt.pack(fill="both", expand=True, padx=5, pady=5)
        
        def run_parse():
            raw = txt.get("1.0", tk.END)
            items = ClipImporter.smart_parse(raw)
            if items:
                for i, t in enumerate(items): self.core.slots[i+1] = t
                self.core._save_slots()
                self.core.current_seq_slot = 1
                self.refresh_ui()
                toast("Ingest", f"Loaded {len(items)} items")
                win.destroy()
                
        tk.Button(win, text="Process Data", command=run_parse).pack(pady=5)

    # --- UTILS ---
    def toggle_hud(self):
        if self.hud:
            self.hud.window.destroy(); self.hud = None
        else:
            self.hud = HudWindow(self.root)
            self.update_hud()

    def update_hud(self):
        if self.hud: self.hud.update_view(self.core.current_seq_slot, self.core.slots)

    def refresh_ui(self):
        self.refresh_slots()
        self.update_hud()

    def refresh_slots(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for slot in range(1, 11):
            text = self.core.slots.get(slot, "")
            preview = (text[:70] + "...") if len(text) > 70 else text.replace("\n", " ")
            display_slot = str(slot)
            if self.mode_var.get() == "sequential" and slot == self.core.current_seq_slot:
                display_slot += " ▶"
            self.tree.insert("", "end", values=(display_slot, preview))

    def clear_all(self):
        if messagebox.askyesno("Clear", "Wipe slots?"):
            self.core.clear_all()
            self.refresh_ui()

    def run(self):
        self.root.geometry("650x450")
        self.root.mainloop()

if __name__ == "__main__":
    MultiClipGUI().run()
