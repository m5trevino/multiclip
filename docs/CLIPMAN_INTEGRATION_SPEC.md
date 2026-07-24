# MultiClip + Clipman Integration Specification

**Date:** 2026-05-21  
**Status:** Current agreed direction  
**Goal:** Turn MultiClip into a practical tool that lets you browse your full Clipman history, selectively move items into the classic 30-slot system, and then use the powerful sequential + batch features from the OG slots — all while keeping the existing hotkey workflow intact.

---

## 1. Core Philosophy

- The **OG 30 Slots** (left side) remain the primary working area for sequencing and batch pasting.
- **Clipman History** (right side) is a powerful browser and source — not the direct place you run sequences from.
- You should be able to work **entirely with hotkeys** (Left Ctrl+Alt + number to copy into OG slots, Right Ctrl+Alt + number to paste from OG slots) without ever touching the UI.
- The UI exists for when you want more control, browsing, and curation.

---

## 2. UI Layout (Current Target)

- **Left side**: Classic dense 30-slot OG Workbench (the layout you like from the old UI).
- **Right side**: Clipman History browser (paginated).
- **Bottom-left area** (under the 30 OG slots): Snippets section (for reusable text like addresses, common commands, etc.). This was requested earlier and should be reserved.

---

## 3. Clipman History Panel (Right Side) — Pagination Rules

- The panel shows entries from your real `~/.cache/xfce4/clipman/textsrc` file.
- It does **not** load the entire 5MB+ file at once (to avoid lag).
- It loads only enough entries to fill the visible area of the panel ("one screen's worth").
- Pagination controls:
  - Next Page
  - Previous Page
  - Ability to jump through all historical pages
- When you move to the next page, only that page's data is loaded.
- When you go back, it reloads the previous page.
- This allows you to scroll through your entire Clipman history one page at a time without performance issues.

---

## 4. Transfer Logic (Moving from Clipman → OG Slots)

This is the most important piece.

### Basic Flow
- You select one or more items in the Clipman History panel.
- You press **Transfer** (button or future hotkey).
- The selected content is moved into the OG 30 slots.

### Smart Fill Rules

1. **Prefer empty slots first**  
   Fill the next empty OG slot(s) in order.

2. **When all OG slots are full**  
   Do **not** error out or crash.  
   Instead:
   - Show a clear warning popup.
   - Tell the user that all slots are occupied.
   - Offer the user the choice to:
     - Pick a specific slot number to overwrite (recommended safest path), **or**
     - Confirm that it should overwrite the oldest slot.

3. **Overwrite behavior**  
   When overwriting is needed (no empty slots and user confirms or picks a slot), the system replaces the content in the chosen slot.  
   The old data is not lost — it still exists in your Clipman history.

---

## 5. Selection & Grouping Behavior (What You're Currently Refining)

- Each row in the current Clipman History list represents one logical Clipman entry.
- Selecting multiple rows = multiple separate items.
- For now (while using the Listbox): each selected row becomes one OG slot.
- You are exploring more granular control:
  - Selecting multiple separate blocks inside one long entry should be able to become multiple slots.
  - A "Lock / Commit" mechanism is desired so you can build multiple groups before transferring.
- A "Transfer as One Slot" option is wanted for cases where you want a large highlighted block (even with newlines) to go into a single OG slot.

These behaviors are still being refined through your screenshots and testing.

---

## 6. OG 30 Slots Behavior

- This is the "working" area.
- You can manually reorder slots.
- You have a **Reset / Normalize** button that puts everything back to default order (1–30).
- All **Sequential** and **Batch** paste features come from here.
- These slots can be overwritten without losing data (because everything lives in Clipman history).

---

## 7. Hotkey Philosophy (Headless Mode)

- You want to be able to use MultiClip all day with almost no UI interaction.
- Current working hotkeys should remain:
  - Left Ctrl + Left Alt + 1-0 → Copy into OG slots
  - Right Ctrl + Right Alt + 1-0 → Paste from OG slots
- Future snippet hotkeys and any new transfer hotkeys will be added later (you'll decide the actual keys).

---

## 8. Snippets Section (Bottom Left)

- Located directly underneath the 30 OG slots.
- For reusable text you type frequently (commands, addresses, templates, signatures, etc.).
- Must support:
  - Add new snippet
  - Edit existing snippet
  - Delete snippet
  - Persistent storage (survives restarts, stored in a file)
- Hotkeys for quick paste will be added later.
- You want to start collecting snippets even before the hotkeys are wired.

---

## 9. Phased Implementation Plan (Recommended Order)

**Phase 0 – Current State (Mostly Done)**
- Old dense 30-slot UI is loading
- Basic Clipman History Listbox panel exists on the right
- Basic transfer from list rows to OG slots
- Working L/R hotkeys for classic copy/paste into OG slots

**Phase 1 – Pagination + Better Transfer (Next Priority)**
- Implement proper pagination in the Clipman History panel (load only current page)
- Improve transfer logic with "all slots full" warning + user choice of target slot
- Add "Transfer as One Slot" button for forcing large blocks into single slots

**Phase 2 – Lock / Commit & Granular Selection**
- Add Lock/Commit mechanism in the Clipman panel
- Explore better ways to handle partial selections inside long entries (while keeping Listbox if you like it)

**Phase 3 – Snippets Area**
- Add the Snippets section in the bottom-left under the OG slots
- Add add/edit/delete + persistence
- Reserve space for future hotkeys

**Phase 4 – Hotkeys & Polish**
- Add hotkeys for new features (snippets, transfer, pagination, etc.)
- Final testing and small UX tweaks

---

## 10. Open Questions / Notes

- Exact button names and wording for warnings can be refined as we build.
- Whether the Clipman panel stays as a Listbox long-term or evolves is still open (you currently like the current behavior).
- Hotkey choices for new features are still undecided (you'll decide when ready).
- We should protect the existing reliable hotkey + paste core at all costs.

---

**Document Owner:** This spec should be updated as decisions are made during implementation.

This file is meant to be the single source of truth for the current direction so we don't lose details as we build.

---

Would you like me to expand any section, turn this into a more formal phased to-do list with estimated effort, or start implementing Phase 1 right away? Just say the word.