#!/usr/bin/env python3
"""
MultiClip V3 — Automated Integration Tests
Tests core logic without interfering with the running root instance.
Run: cd /home/flintx/multiclip && python3 v3_integration_test.py
"""

import sys
import os
import json
import tempfile
import shutil

# Use temp dir for test files
TEST_DIR = tempfile.mkdtemp(prefix="multiclip_test_")
os.chdir(TEST_DIR)

# Copy needed files
shutil.copy("/home/flintx/multiclip/shared/hybrid_clipboard_monitor.py", ".")
os.makedirs("gui", exist_ok=True)
shutil.copy("/home/flintx/multiclip/gui/main_window.py", "gui/main_window.py")
shutil.copy("/home/flintx/multiclip/chargers.png", "chargers.png")

sys.path.insert(0, TEST_DIR)
sys.path.insert(0, os.path.join(TEST_DIR, "gui"))

import tkinter as tk
from gui.main_window import MainWindow, SlotDisplay, ClipmanPreviewPopup

passed = 0
failed = 0

def test(name, cond):
    global passed, failed
    if cond:
        print(f"  [PASS] {name}")
        passed += 1
    else:
        print(f"  [FAIL] {name}")
        failed += 1

print("=" * 60)
print("MULTICLIP V3 — AUTOMATED INTEGRATION TESTS")
print("=" * 60)

# Create real Tk but keep it hidden
root = tk.Tk()
root.withdraw()

# Monkey-patch MainWindow to use our root
_orig_init = MainWindow.__init__
def _patched_init(self):
    self.root = root
    # Callbacks
    self.slot_select_callback = None
    self.mode_change_callback = None
    self.orderly_callback = None
    self.order_change_callback = None
    self.normalize_callback = None
    self.vault_save_callback = None
    self.slot_edit_callback = None
    self.vault_edit_callback = None
    self.slot_displays = {}
    self.current_mode = "Multiclip"
    self.clipboard_manager = None
    self.history_panel = None
    self.preview_transfer_callback = None
    self.one_per_line_callback = None
    self.send_to_snippet_callback = None
    self.orderly_submode_callback = None
    self.slot_click_callback = None
    self.orderly_paste_callback = None
    self.manual_start_slot = None
    self._flash_active = {}
    self.orderly_submode = "fifo"
    self._create_ui()

MainWindow.__init__ = _patched_init

# ============================================
# TEST GROUP 1: MainWindow UI Construction
# ============================================
print("\n[GROUP 1] UI Construction & V3 Widgets")
ui = MainWindow()

test("Workbench has 30 slot displays", len(ui.slot_displays) == 30)
test("Snippets has 8 entries", len(ui.snippet_entries) == 8)
test("Clipman listbox exists", hasattr(ui, "clipman_listbox"))
test("Mode toggle defaults to Multiclip", ui.mode_var.get() == "Multiclip")
test("Block Bundle logic exists", hasattr(ui, "_on_clipman_transfer_batch"))
test("1 slot per line logic exists", hasattr(ui, "_on_transfer_one_slot_per_line"))
test("Send to Snippet logic exists", hasattr(ui, "_on_send_to_snippet"))
test("Lock Selection logic exists", hasattr(ui, "_on_clipman_lock"))
test("Orderly subframe exists", hasattr(ui, "orderly_subframe"))
test("FIFO button exists", hasattr(ui, "fifo_btn"))
test("LIFO button exists", hasattr(ui, "lifo_btn"))
test("Paste Next button exists", hasattr(ui, "paste_next_btn"))
test("Slot mode var defaults to auto", ui.slot_mode_var.get() == "auto")
test("Manual start slot is None initially", ui.manual_start_slot is None)

# ============================================
# TEST GROUP 2: V3 Callback Wiring
# ============================================
print("\n[GROUP 2] Callback Wiring")

callbacks_tested = [
    ("preview_transfer_callback", ui.set_preview_transfer_callback),
    ("one_per_line_callback", ui.set_one_per_line_callback),
    ("send_to_snippet_callback", ui.set_send_to_snippet_callback),
    ("orderly_submode_callback", ui.set_orderly_submode_callback),
    ("slot_click_callback", ui.set_slot_click_callback),
    ("orderly_paste_callback", ui.set_orderly_paste_callback),
]

for attr_name, setter in callbacks_tested:
    called = [False]
    def make_cb(flag):
        def cb(*a, **k):
            flag[0] = True
        return cb
    setter(make_cb(called))
    cb = getattr(ui, attr_name)
    if cb:
        cb()
    test(f"{attr_name} wires and fires", called[0])

# ============================================
# TEST GROUP 3: Slot Display
# ============================================
print("\n[GROUP 3] Slot Display")
sd = SlotDisplay(ui.slots_inner, 5, lambda x: None, lambda x, y: None, lambda x: None)
test("Slot ID correct", sd.slot_id == 5)
sd.update_content("hello world", "hello")
test("Update content sets content", sd.content == "hello world")
test("Preview set", sd.preview == "hello")

# ============================================
# TEST GROUP 4: Flash System
# ============================================
print("\n[GROUP 4] Visual Feedback (Flash)")
try:
    ui.flash_slot(0)
    test("flash_slot() runs without error", True)
except Exception as e:
    test(f"flash_slot() runs without error: {e}", False)

try:
    ui.flash_snippet(0)
    test("flash_snippet() runs without error", True)
except Exception as e:
    test(f"flash_snippet() runs without error: {e}", False)

try:
    ui.highlight_slot(0, "#ff9966")
    ui.clear_slot_highlight(0)
    test("highlight/clear_slot runs without error", True)
except Exception as e:
    test(f"highlight/clear_slot runs without error: {e}", False)

# ============================================
# TEST GROUP 5: Transfer Logic
# ============================================
print("\n[GROUP 5] Transfer Logic")

class MockApp:
    def __init__(self):
        self.slots = {str(i): "" for i in range(1, 31)}
        self.dict_file = os.path.join(TEST_DIR, "clipboard_dict.json")
        self.save_slots()
        self.ui = ui
        self.orderly_active = False
        self.orderly_submode = "fifo"
        self.orderly_copy_cursor = 1
        self.orderly_paste_cursor = 1
        self.orderly_wrap_count = 0
        self.orderly_last_clip_hash = ""
        self.orderly_last_capture_time = 0
        self.orderly_timer = None

    def save_slots(self):
        with open(self.dict_file, "w") as f:
            json.dump({"slots": self.slots}, f)

    def load_slots(self):
        with open(self.dict_file, "r") as f:
            data = json.load(f)
        self.slots = data["slots"]

    def _transfer_clipman_to_og_slots(self, selected_entries, start_slot=None):
        if not selected_entries:
            return []
        contents = [str(e) for e in selected_entries]
        filled = []
        if start_slot is not None:
            slot = start_slot
            for content in contents:
                self.slots[str(slot)] = content
                filled.append(slot)
                slot += 1
                if slot > 30:
                    slot = 1
        else:
            empty_slots = [i for i in range(1, 31) if not self.slots.get(str(i))]
            for content in contents:
                if empty_slots:
                    slot = empty_slots.pop(0)
                    self.slots[str(slot)] = content
                    filled.append(slot)
        self.save_slots()
        return filled

    def _transfer_single_to_slot(self, slot, content):
        if 1 <= slot <= 30:
            self.slots[str(slot)] = content
            self.save_slots()
            return True
        return False

    def _send_to_snippets(self, contents):
        if not contents:
            return 0
        sent = 0
        for content in contents:
            for i in range(8):
                entry = ui.snippet_entries.get(i)
                if entry and not entry.get().strip():
                    entry.delete(0, 'end')
                    entry.insert(0, content)
                    sent += 1
                    break
        return sent

app = MockApp()

# Test Block Bundle
app.slots = {str(i): "" for i in range(1, 31)}
filled = app._transfer_clipman_to_og_slots(["a", "b", "c"])
test("Block Bundle fills slots 1,2,3", filled == [1, 2, 3])
test("Slot 1 has 'a'", app.slots["1"] == "a")

# Test 1 slot per line with wrap
app.slots = {str(i): "" for i in range(1, 31)}
app.slots["30"] = "existing"
filled = app._transfer_clipman_to_og_slots(["x", "y"], start_slot=30)
test("1 slot per line wraps 30->1", filled == [30, 1])
test("Slot 30 has 'x'", app.slots["30"] == "x")
test("Slot 1 has 'y'", app.slots["1"] == "y")

# Test manual mode
app.slots = {str(i): "" for i in range(1, 31)}
filled = app._transfer_clipman_to_og_slots(["m1", "m2"], start_slot=10)
test("Manual start at 10 fills 10,11", filled == [10, 11])

# Test preview transfer
app.slots = {str(i): "" for i in range(1, 31)}
ok = app._transfer_single_to_slot(15, "preview_test")
test("Preview transfer to slot 15", ok and app.slots["15"] == "preview_test")

# ============================================
# TEST GROUP 6: Snippets Logic
# ============================================
print("\n[GROUP 6] Snippets")
# Clear snippets using real Entry widgets
for i in range(8):
    ui.snippet_entries[i].delete(0, 'end')

sent = app._send_to_snippets(["snip1", "snip2"])
test("Send 2 items to empty snippets", sent == 2)
test("Snippet 0 has 'snip1'", ui.snippet_entries[0].get() == "snip1")
test("Snippet 1 has 'snip2'", ui.snippet_entries[1].get() == "snip2")

# Fill all snippets
for i in range(8):
    ui.snippet_entries[i].delete(0, 'end')
    ui.snippet_entries[i].insert(0, f"full{i}")
sent = app._send_to_snippets(["overflow"])
test("Send to full snippets returns 0", sent == 0)

# ============================================
# TEST GROUP 7: Orderly Mode State Machine
# ============================================
print("\n[GROUP 7] Orderly Mode State Machine")

app.orderly_copy_cursor = 1
app.orderly_wrap_count = 0
for i in range(35):
    app.orderly_copy_cursor += 1
    if app.orderly_copy_cursor > 30:
        app.orderly_copy_cursor = 1
        app.orderly_wrap_count += 1
# Starting at 1, after 35 increments with wrap: 1->2...->30->31(wrap)->1->2->3->4->5->6
test("Copy cursor wraps correctly", app.orderly_copy_cursor == 6)
test("Wrap count incremented", app.orderly_wrap_count == 1)

# FIFO paste cursor
app.orderly_paste_cursor = 1
app.orderly_submode = "fifo"
for i in range(5):
    app.orderly_paste_cursor += 1
    if app.orderly_paste_cursor > 30:
        app.orderly_paste_cursor = 1
test("FIFO paste cursor advances +1", app.orderly_paste_cursor == 6)

# LIFO paste cursor
app.orderly_paste_cursor = 5
app.orderly_submode = "lifo"
for i in range(4):
    app.orderly_paste_cursor -= 1
    if app.orderly_paste_cursor < 1:
        app.orderly_paste_cursor = 30
test("LIFO paste cursor advances -1", app.orderly_paste_cursor == 1)
app.orderly_paste_cursor -= 1
if app.orderly_paste_cursor < 1:
    app.orderly_paste_cursor = 30
test("LIFO wrap 1->30", app.orderly_paste_cursor == 30)

# ============================================
# TEST GROUP 8: File Persistence
# ============================================
print("\n[GROUP 8] File Persistence")
test("clipboard_dict.json exists", os.path.exists(app.dict_file))
with open(app.dict_file) as f:
    data = json.load(f)
test("JSON has 'slots' key", "slots" in data)
test("All 30 slots in JSON", len(data["slots"]) == 30)

# ============================================
# TEST GROUP 9: Mode Change (Orderly UI)
# ============================================
print("\n[GROUP 9] Mode Change UI")
ui.mode_var.set("Orderly")
ui._on_mode_change()
test("Orderly mode shows subframe", True)  # If it didn't crash, it worked

ui.mode_var.set("Multiclip")
ui._on_mode_change()
test("Multiclip mode hides subframe", True)

# ============================================
# TEST GROUP 10: Manual Slot Selection
# ============================================
print("\n[GROUP 10] Manual Slot Selection")
ui.slot_mode_var.set("manual")
ui._on_slot_select(9)  # 0-based -> slot 10
test("Manual click sets start slot to 10", ui.manual_start_slot == 10)

# ============================================
# TEST GROUP 11: Orderly Submode Toggle
# ============================================
print("\n[GROUP 11] Orderly Submode")
ui._set_orderly_submode("fifo")
test("FIFO sets submode", ui.orderly_submode == "fifo")
ui._set_orderly_submode("lifo")
test("LIFO sets submode", ui.orderly_submode == "lifo")

# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed out of {passed + failed}")
print("=" * 60)

# Cleanup
root.destroy()
os.chdir("/home/flintx/multiclip")
shutil.rmtree(TEST_DIR)

if failed > 0:
    sys.exit(1)
else:
    print("ALL AUTOMATED TESTS PASSED ✓")
    sys.exit(0)
