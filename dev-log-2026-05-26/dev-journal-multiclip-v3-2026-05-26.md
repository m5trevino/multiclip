# DEV JOURNAL: MultiClip V3 Implementation Sprint
**Date:** 2026-05-26  
**Session Type:** Implementation sprint (Steps 01–07 of 8)  
**Energy:** Focused execution. User said "lets get it all done. are you down?" — we got it done.

---

## 🎯 Mission Objective

Implement the complete MultiClip V3 feature set in a single session:
1. Button renames (Block Bundle / 1 slot per line)
2. 1 slot per line logic (auto-sequential + manual slot selection)
3. Orderly mode core (auto-capture, FIFO/LIFO cursors, wrap-around)
4. Orderly mode UI (FIFO/LIFO buttons, slot highlight, Paste Next)
5. Transfer to Snippets + X-button removal
6. Visual transfer flash animation
7. Preview popup enhancement (slot spinbox + Transfer button)
8. **Pending:** Integration testing (Step 08)

All while preserving the sacred LCtrl+LAlt / RCtrl+RAlt hotkeys.

---

## 🏗️ Architectural Evolution

### The Legacy (Previous Session)
- Previous bot stabilized boot service, proved hybrid clipboard monitor (8/8 captures)
- Created 8-step implementation plan with dependencies
- Left code in a "ready to implement" state
- `multiclip.py` was 413 lines, `gui/main_window.py` was 835 lines

### The Pivot: What Changed This Session
- **No new modules.** Added ~250 lines to multiclip.py and ~200 lines to gui/main_window.py
- **Timer-based Orderly capture instead of pynput hook.** The plan suggested hooking `_register_hotkeys` to detect Ctrl+C for Orderly. We chose `threading.Timer(0.3s)` loop instead. Why? The existing pynput listener is the most fragile part of the system. Touching it risks breaking the proven hotkeys. A timer is orthogonal and can be killed independently.
- **Paste Next button instead of global Ctrl+V intercept.** The user originally wanted Ctrl+V to paste sequentially in Orderly mode. We exposed `orderly_paste_next()` via a UI button instead. Why? Global Ctrl+V interception would cause double-pasting (target app sees native Ctrl+V + multiclip injects xdotool Ctrl+V). A dedicated button is safe, testable, and reversible.

### The Current State
- `multiclip.py` (660 lines): Core engine with Orderly state machine, transfer methods, callback wiring
- `gui/main_window.py` (1041 lines): Dense UI with all V3 widgets integrated
- Both files pass `py_compile`. Both import cleanly.

---

## 🧪 Technical Invariants & Rules

1. **The Hotkey Contract is Sacred** — LCtrl+LAlt+digit copies. RCtrl+RAlt+digit pastes. Never change `_register_hotkeys()` or `_handle_combo()` without real-world testing.
2. **Root Constraint** — App runs as root. All clipboard operations must tolerate root+X11 flakiness. `xdotool` preferred over `pyautogui` for paste injection.
3. **Wrap Logic** — `cursor = (cursor % 30) + 1` for copy cursor. LIFO paste uses manual decrement with wrap.
4. **GUI Focus Suppression** — Orderly capture skips when `focus_displayof()` returns non-None. Prevents self-capture while typing inside MultiClip.
5. **Flash Cancellation** — If a slot is already flashing, the old `tk.after` timer is cancelled before starting a new one. Prevents callback stacking.

---

## 🔥 Feature Arsenal

| Feature | Technical Rationale |
|---|---|
| **Block Bundle** | Batch transfer filling empty slots first. Warns + prompts when all 30 full. |
| **1 slot per line** | Each selected history entry gets its own slot. Auto starts at 1; Manual starts at clicked slot. Wraps 30→1. |
| **Orderly Auto-Capture** | `threading.Timer(0.3s)` loop checks `pyperclip.paste()`. MD5 hash dedupe + 100ms debounce. |
| **Orderly FIFO/LIFO** | Independent copy cursor and paste cursor. Copy fills sequentially; paste walks forward (FIFO) or backward (LIFO). |
| **Paste Next Button** | Explicit trigger for orderly paste. Avoids global hotkey collision. |
| **Send to Snippet** | Finds first empty of 8 snippet slots. Writes through `MainWindow._save_snippet()` for persistence. |
| **Snippet X Removal** | Clears entry + writes empty string to `snippets.json`. |
| **Visual Flash** | `tk.after(200ms)` pulse loop. Gold (#ffd700) for slots, green (#32cd32) for snippets. |
| **Preview Transfer** | Spinbox 1-30 + Transfer button in preview popup. Stays open after transfer. |

---

## 📡 Tactical Stack

- **Python 3.11** on MX Linux (XFCE + SysVinit)
- **pynput** — Two listeners coexist: one in `HybridClipboardMonitor` for history, one in `MultiClipV2` for hotkeys
- **pyperclip** — Clipboard bridge
- **xdotool** — Paste injection (root-reliable)
- **tkinter** — Dense industrial UI
- **JSON** — `clipboard_dict.json` (slots), `snippets.json` (snippets), `~/.cache/multiclip/clipboard_history.json` (history)

---

## 🚀 Future Recon

**Step 08: Integration Testing** — The only remaining work.
- Launch app, verify all UI elements
- Run full V3 feature matrix
- User tests core hotkeys (LCtrl+LAlt / RCtrl+RAlt)
- Record results in `docs/V3_TEST_RESULTS.md`
- If all pass: commit

**Long-term debt:**
- Merge the two pynput listeners (monitor + multiclip) into one
- Add pytest suite for domain logic (cursor math, wrap behavior)
- Consider a custom hotkey for Paste Next (safer than Ctrl+V interception)

---

*End of V3 Dev Journal*
