# Multiclip Questionnaire Answers — Compiled Reference

> **Source:** Extracted from session wire logs (`affccbf6-066c-4166-ab88-11977c1425c8`)
> **Note:** When user selects option 4 ("Other"), they type a custom response. Options 1-3 are straight selections.

---

## Questionnaire 1 — Feature Priority (line 243)

**Q: Should I proceed with all the fixes and features?**

| Option | Label | User Choice |
|--------|-------|-------------|
| 1 | Yes, do everything | |
| 2 | **Just fix boot + live refresh first** | **SELECTED** |
| 3 | Only fix the boot issue | |

**Verdict:** Start with bug fixes (dual instance + live refresh), then UI features after.

---

## Questionnaire 2 — Pagination & Preview (line 415)

**Q1: Pagination — how many items per page?**
- **Answer:** 50 per page (current default)

**Q2: Pagination controls — where and how?**
- **Answer:** Both arrows + page counter (Prev / Page 3 of 12 / Next)

**Q3: Double-click preview popup — close behavior?**
- **Answer:** Both (click outside OR X button)

**Q4: Multi-select preview — how to show multiple selected items?**
- **Answer:** Both options above (one popup with all items stacked + prev/next inside popup)

---

## Questionnaire 3 — Orderly Mode UI (line 653)

**Q1: Where should Auto-Sequential / Manual toggle live when "1 slot per line" mode is active?**
- **Answer (Option 4 — custom):** Image provided (`jbtngpbs.png`, 1098x863). Buttons should appear with unique colors for easy access. They show up when Orderly mode is set. User wants colored buttons that are visually obvious — when Clipman highlights something in a color, that same color indicates what mode is active. Put instructions in the top-left question mark help button.

**Q2: Where should FIFO/LIFO toggle live when Orderly mode is selected?**
- **Answer (Option 4 — custom):** User got questions mixed up. FIFO/LIFO toggles should be "already there in the top left above the work bench slots" — visible in the toolbar area near the Orderly mode button.

**Q3: Should the Orderly queue be saved to disk or lost on restart?**
- **Answer (Option 4 — custom):** Detailed spec:
  - Orderly mode ON → starts from slot 1 unless user manually changes starting slot in workbench
  - Every Ctrl+C copy goes to the **next slot after the last copied slot**
  - Ctrl+V keeps pasting from where it left off
  - **Example:** copied slots 1-60, pasted slots 60-67, then copied 70-80 → next Ctrl+V pastes slot 68
  - The "next paste slot" should always be **highlighted/lit up** in the workbench slots
  - Copy cursor and paste cursor are **independent**

**Q4: How should snippet removal work?**
- **Answer:** Both (clear text + hit Save AND dedicated X button per snippet)

---

## Questionnaire 4 — Orderly Mode Details (line 671)

**Q1: For "1 slot per line" mode — where does Auto-Sequential / Manual toggle go?**
- **Answer (Option 4 — custom):** Image provided (`obgrjdhu.png`, 1110x885). Manual toggle: user selects a workbench slot by clicking it. The slot changes to the same color as the Sequential radio toggle (make it a unique color). This makes it obvious what mode is active. Instructions go in the top-left question mark help button.

**Q2: When Orderly mode fills all 30 slots, what happens next?**
- **Answer:** Wrap around to slot 1 (overwrite oldest)

**Q3: How many Orderly sub-mode buttons?**
- **Answer:** 2 buttons: FIFO and LIFO

---

## Subagent Questionnaires (Confirm Context)

These were context-validation questions asking "Does this match your intent?" — all answered affirmatively (implied by session continuation).

---

## Consolidated Feature Spec from Answers

### Boot & Live Refresh (Phase 1 — DONE)
- Fix boot duplication (systemd + autostart conflicts)
- Add single-instance guard (lock file with `fcntl.flock`)
- Live Clipman refresh via polling `textsrc` mtime

### Pagination & History Panel (Phase 2)
- 50 items per page
- Prev / Page X of Y / Next controls
- Wire up dormant `HistoryPanel` to replace simple Listbox
- Live refresh must work with HistoryPanel

### Double-Click Preview Popup
- Shows full text of clip
- Close by clicking outside OR X button
- Multi-select: stacked view of all selected items + prev/next navigation inside popup

### Orderly Mode (Advanced)
- **2 buttons:** FIFO and LIFO (in toolbar near workbench)
- **Wrap around:** When slot 30 is full, overwrite slot 1 (circular buffer)
- **Independent cursors:**
  - Copy cursor: next slot after last copied
  - Paste cursor: where next Ctrl+V will paste from
  - Paste cursor slot always highlighted/lit in workbench
- **Manual mode:** User clicks a workbench slot to set starting point
- **Auto-Sequential mode:** Lines fill next available slots automatically
- **Colored UI:** Each mode has unique color. Selected slot glows with Sequential toggle color

### Snippets Panel
- Both clear+save AND X button per snippet for removal

### Transfer Features
- Transfer selected Clipman items to specific workbench slot
- Transfer selected Clipman items to snippets

---

## Open Questions (Not Yet Asked)

1. What colors for each mode? (Sequential, FIFO, LIFO, Manual)
2. Should Orderly queue persist across reboots? (User wants volatile — resets on boot)
3. Keyboard shortcuts for Orderly mode toggles?
4. Should the popup also allow editing the clip text before transfer?
