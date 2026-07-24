# Hand-Off Report — multiclip
**Task:** Implement MultiClip V3 features (Steps 01–07) + integration prep  
**Status:** Code complete — ready for Step 08 integration testing  
**Date:** 2026-05-26  
**Session:** Post-rehab V3 implementation sprint  

---

## Boot Sequence (READ THESE FIRST)
1. Read `multiclip.py` — 660 lines, core engine with Orderly mode, hybrid monitor, V3 callbacks
2. Read `gui/main_window.py` — 1041 lines, dense UI with all V3 widgets
3. Read `shared/hybrid_clipboard_monitor.py` — proven clipboard capture (pynput + poll)
4. Run `python3 -m py_compile multiclip.py gui/main_window.py` to verify syntax
5. Check `docs/V3_TEST_RESULTS.md` for current test status (create if not exists)

---

## What Was Done This Session

| Step | Feature | Status | Files |
|------|---------|--------|-------|
| 01 | Button renames (Block Bundle / 1 slot per line) + Auto/Manual toggle | ✅ Done | gui/main_window.py |
| 02 | 1 slot per line logic (auto-sequential + manual slot selection with wrap) | ✅ Done | multiclip.py + gui/main_window.py |
| 03 | Orderly mode core (300ms timer auto-capture, FIFO/LIFO cursors, wrap at 30) | ✅ Done | multiclip.py |
| 04 | Orderly mode UI (FIFO/LIFO buttons, next-slot gold highlight, Paste Next button) | ✅ Done | gui/main_window.py |
| 05 | Transfer to Snippets + X-button removal | ✅ Done | multiclip.py + gui/main_window.py |
| 06 | Visual transfer flash (~2s gold pulse on slots, green on snippets) | ✅ Done | gui/main_window.py |
| 07 | Preview popup enhancement (slot spinbox 1-30 + Transfer button) | ✅ Done | gui/main_window.py |
| 08 | Integration testing + user hotkey verification | ⏳ Pending | — |

---

## Files Changed (Uncommitted)

| File | Lines | Key Changes |
|------|-------|-------------|
| `multiclip.py` | 660 | Added Orderly state machine, `_transfer_clipman_to_og_slots` with `start_slot`, `_transfer_single_to_slot`, `_send_to_snippets`, `_refresh_slot_displays`, `_orderly_tick` / `_orderly_clip_check` / `orderly_paste_next`, `_is_gui_focused`, all callback wiring |
| `gui/main_window.py` | 1041 | Renamed buttons, added mode toggle, orderly subframe (FIFO/LIFO/Paste Next), snippet X buttons, Send to Snippet button, `flash_slot` / `flash_snippet` / `highlight_slot` / `clear_slot_highlight`, preview popup transfer bar, manual slot selection logic, all callback setters |

**Backups created:** `multiclip.py.bak`, `gui/main_window.py.bak`

---

## Architecture Changes

### New Callback Wiring (multiclip.py ↔ gui/main_window.py)
```
multiclip.py._wire_old_ui() wires these callbacks into MainWindow:
- set_preview_transfer_callback   → _transfer_single_to_slot(slot, content)
- set_one_per_line_callback       → _transfer_clipman_one_per_line(entries, start_slot)
- set_send_to_snippet_callback    → _send_to_snippets(contents)
- set_orderly_submode_callback    → _set_orderly_submode(mode)
- set_slot_click_callback         → _on_manual_slot_clicked(slot_id)
- set_orderly_paste_callback      → orderly_paste_next()
- mode_change_callback            → _on_mode_change(mode)
```

### Orderly Mode Data Flow
```
User selects "Orderly" radio → _on_mode_change("Orderly") → start_orderly_monitor()
  → threading.Timer(0.3s) loop → _orderly_clip_check()
    → pyperclip.paste() → hash dedupe → fill slot → flash → advance cursor (wrap 30→1)
    → highlight next copy slot in orange (#ff9966)
    → update status bar: "Queue: N items | Next: Slot XX"

User clicks "Paste Next" → orderly_paste_next()
  → pyperclip.copy(slot content) → xdotool paste injection
  → advance paste cursor (FIFO +1, LIFO -1, wrap)
  → highlight next paste slot in green (#66ff66)
```

---

## Exact Next Action (Step 08)

1. **Launch the app:** `cd /home/flintx/multiclip && python3 multiclip.py &`
2. **Verify UI loads** with all V3 elements visible:
   - Workbench 30 slots (left)
   - Snippets 8 rows with X buttons (bottom-left)
   - Clipman History panel (right) with Block Bundle, 1 slot per line, Send to Snippet, Lock Selection
   - Mode toggle (Auto-Sequential / Manual Slot) under 1 slot per line button
   - FIFO/LIFO buttons + Paste Next button appear only in Orderly mode
3. **Run full V3 feature matrix** (see `docs/V3_TEST_RESULTS.md` template below)
4. **User tests hotkeys** — LCtrl+LAlt+digit and RCtrl+RAlt+digit must still work
5. **Record results** in `docs/V3_TEST_RESULTS.md`

---

## V3 Feature Matrix (for Step 08)

| Feature | Test Action | Expected Result |
|---|---|---|
| Block Bundle | Select 3 history items, click Block Bundle | 3 slots filled, gold flash |
| 1 slot per line (Auto) | Select 2 items, mode=Auto, click 1 slot per line | Slots fill from 1 upward |
| 1 slot per line (Manual) | Click slot 10, select 2 items, mode=Manual, click 1 slot per line | Slots 10, 11 filled |
| Orderly capture | Activate Orderly, copy text externally | Auto-fills next slot, flashes gold |
| Orderly FIFO paste | Fill slots 1-3, click Paste Next | Pastes 1, then 2, then 3 |
| Orderly LIFO paste | Fill slots 1-3, switch LIFO, click Paste Next | Pastes 3, then 2, then 1 |
| Send to Snippet | Select item, click Send to Snippet | Lands in first empty snippet, green flash |
| Snippet X remove | Click X on a snippet | Entry clears, persists |
| Visual flash | Any transfer above | Destination pulses gold/green |
| Preview transfer | Double-click item, enter slot 15, Transfer | Slot 15 filled, popup stays open |
| Slots full dialog | Fill all 30, attempt transfer | Warning dialog appears |

---

## Decisions Made

- **Paste Next button vs global Ctrl+V intercept:** Chose a "Paste Next" button in the Orderly subframe instead of globally intercepting Ctrl+V. Global Ctrl+V interception risks double-pasting (app sees native Ctrl+V + multiclip injects another). A dedicated button is safer and testable. Can be upgraded to a custom hotkey later.
- **Timer-based Orderly capture:** Used `threading.Timer(0.3s)` loop in multiclip.py rather than hooking the existing pynput listener. This avoids touching the sacred hotkey logic.
- **Manual slot selection:** Clicking a Workbench slot while "Manual Slot" mode is active sets `manual_start_slot` and highlights the slot blue.

---

## Known Issues / Risks

1. **Two pynput listeners running:** `HybridClipboardMonitor` starts its own listener for history capture. `multiclip.py` starts another for hotkeys. They coexist but this is not ideal long-term.
2. **Orderly capture may miss rapid copies:** 300ms timer + 100ms debounce means copies faster than ~400ms apart might be missed.
3. **GUI focus suppression:** `_is_gui_focused()` uses `focus_displayof()` which may have edge cases on X11.
4. **No automated tests:** All testing is manual. No pytest suite exists.

---

## Guardian Context

- **CRITICAL:** `pyautogui.FAILSAFE = False` is still set. Dangerous but required for root operation.
- **Root constraint:** App must run as root for global hotkeys. X11 cookie copy to `/tmp/.Xauthority_multiclip` is still in place.
- **textsrc is DEPRECATED:** `HybridClipboardMonitor` captures to `~/.cache/multiclip/clipboard_history.json`. Never read textsrc again.
- **Scope creep trap:** This project has died from over-engineering before. Only Step 08 remains. Do not add new features until Step 08 passes.
