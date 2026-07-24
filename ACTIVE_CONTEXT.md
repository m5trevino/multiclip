# ACTIVE_CONTEXT — MultiClip

> **Project:** /home/flintx/multiclip  
> **Status:** V3 Steps 01–07 code complete. Step 08 (integration testing) pending.  
> **Last Updated:** 2026-05-26  

---

## Active Projects

| Project | Status | Next Action | Priority |
|---|---|---|---|
| MultiClip V3 | Code complete | Step 08: Run V3 feature matrix + user hotkey test | Critical |

---

## Pending Tasks (by priority)

1. **Step 08: Integration Testing**
   - Launch app, verify all V3 UI elements visible
   - Run full feature matrix (see `docs/V3_TEST_RESULTS.md`)
   - User tests LCtrl+LAlt / RCtrl+RAlt hotkeys
   - Record results, fix any failures, commit

2. **Post-V3 cleanup**
   - Merge two pynput listeners (monitor + multiclip)
   - Add pytest suite for domain logic
   - Remove dead code (`shared/clipboard_manager.py`, `shared/snippets_manager.py`)

---

## Decisions

- **Timer-based Orderly capture** — Uses `threading.Timer(0.3s)` instead of hooking pynput listener. Safer, independent, killable.
- **Paste Next button** — Explicit UI button for orderly paste. Avoids global Ctrl+V double-paste risk.
- **Manual slot selection** — Click Workbench slot while "Manual Slot" mode active to set start point. Blue highlight confirms.

---

## Files Modified (Latest Session)

- `multiclip.py` — Added Orderly core, transfer methods, callback wiring
- `gui/main_window.py` — Added all V3 widgets, flash system, preview transfer
- `HANDOFF.md` — Updated
- `docs/session-handoff-output.md` — Created
- `docs/standard-output.md` — Created
- `docs/deepdive-output.md` — Updated
- `docs/V3_TEST_RESULTS.md` — Created (template)

---

## Blockers

None.

---

## Conventions

- Root execution required for global hotkeys
- `xdotool` preferred over `pyautogui` for paste injection
- Never modify `_register_hotkeys()` or `_handle_combo()` without testing
- Wrap logic: `cursor = (cursor % 30) + 1`

---

## Quick Reference

```bash
# Launch
cd /home/flintx/multiclip && python3 multiclip.py &

# Syntax check
python3 -m py_compile multiclip.py gui/main_window.py

# Restart service
sudo /etc/init.d/multiclip restart

# Test matrix
cat docs/V3_TEST_RESULTS.md
```

---

*Auto-generated for context-agent continuity.*
