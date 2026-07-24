# MultiClip + Clipman Integration — Implementation Plan

**Project:** MultiClip (MX Linux)  
**Date:** 2026-05-21  
**Status:** Ready for execution  
**Goal:** Add deep Clipman history support with pagination, smart transfer, sequencing/batch from OG slots, and a persistent Snippets area — while keeping the existing reliable hotkey workflow intact.

---

## Guiding Principles

- Keep the project **small and practical** (user’s explicit request).
- Protect the **working core** (current hotkeys + paste reliability) at all costs.
- Use the **old dense 30-slot UI** layout as the base (user likes it).
- Clipman History = source / browser.
- OG 30 Slots = working area for sequencing and batch.
- Move in small, testable steps. No massive rewrites.

---

## Phase 0 — Current State (Mostly Done)

- [x] Old dense UI from `gui/main_window.py` is loading via `multiclip.py`
- [x] Basic Clipman History Listbox panel added on the right side
- [x] Basic transfer from selected Clipman rows to OG slots (simple version)
- [x] Working LCtrl+LAlt and RCtrl+RAlt hotkeys for classic copy/paste into OG slots
- [x] Improved `clipman_parser.py` that can reliably read the user’s real textsrc
- [x] `CLIPMAN_INTEGRATION_SPEC.md` created (vision + rules)

**Status:** Foundation is stable. We can now build on top of it.

---

## Phase 1 — Pagination + Smart Transfer (Next Priority)

### 1.1 Clipman History Pagination
- [ ] Implement proper pagination in the right-side Clipman panel.
- [ ] Load only enough entries to fill the visible area (“one screen worth”).
- [ ] Add **Next Page** and **Previous Page** buttons.
- [ ] Only load the current page’s data (lazy loading).
- [ ] When user changes page, unload previous page and load the new one.
- [ ] Allow user to scroll through their entire history (5MB+ file) without lag.

**Dependencies:** Current parser works well enough.

### 1.2 Smart Transfer Logic (Full Slots Handling)
- [ ] Update transfer so it first fills any empty OG slots.
- [ ] When all 30 OG slots are full:
  - Show a clear **warning popup**.
  - Let the user either:
    - Type a specific slot number to overwrite, **or**
    - Confirm overwrite of the oldest slot.
- [ ] Never crash or silently fail when slots are full.

**Dependencies:** 1.1 (pagination) is nice-to-have but not strictly required for this task.

### 1.3 “Transfer as One Slot” Button
- [ ] Add a second button in the Clipman History panel: **“Transfer as One Slot”**.
- [ ] This forces the currently highlighted/selected text (even if multi-line) into a **single OG slot**.

---

## Phase 2 — Lock / Commit & Granular Selection

- [ ] Add a **“Lock Selection”** button in the Clipman History panel.
- [ ] When pressed, the current selection is committed as a group.
- [ ] User can then make a new selection without losing the locked group.
- [ ] On transfer, locked groups are respected (each group becomes one or more slots depending on internal breaks).
- [ ] Decide whether to keep the current Listbox or move to a line-by-line / text-selection view for more granular control.

**Dependencies:** Phase 1 transfer logic should be solid first.

---

## Phase 3 — Snippets Area (Bottom Left)

- [ ] Add a new section directly **underneath the 30 OG slots** (bottom-left area).
- [ ] Call it **Snippets** (or “Quick Snippets”).
- [ ] Features:
  - Add new snippet (name + content)
  - Edit existing snippet
  - Delete snippet
  - Persistent storage (saved to disk, survives restarts)
- [ ] Reserve space for future hotkeys (user will decide keys later).
- [ ] User can start adding snippets immediately, even before hotkeys exist.

**Dependencies:** None — can be done in parallel with other phases.

---

## Phase 4 — Hotkeys & Polish

- [ ] Add hotkeys for new features (once user decides on them):
  - Sequential paste trigger
  - Batch paste trigger
  - Transfer from Clipman (if wanted)
  - Lock / Commit
  - Pagination (next/previous page)
  - Snippet paste hotkeys
- [ ] Add **Reset / Normalize** button for OG slots (if not already working well).
- [ ] Final testing with real usage (hotkeys + UI).
- [ ] Small UX tweaks based on actual use.

---

## Phase 5 — Future / Nice-to-Haves (Do Not Start Yet)

- Deeper intra-entry text selection (if Listbox becomes too limiting).
- Named sequences / multiple saved sequences.
- Better search in Clipman History.
- Visual indicators (which OG slots came from Clipman recently, etc.).
- Export / backup of curated sequences.

---

## Open Questions / Decisions Still Needed

- Exact button names and warning messages (we can refine as we build).
- Whether to keep the Listbox long-term or switch to a different viewer for better line-level selection.
- Exact hotkeys for new features (user will decide when ready).
- How many snippets should be easily visible vs scrollable.

---

## Document Control

- This plan should be updated after each completed phase.
- Major decisions should be recorded in `CLIPMAN_INTEGRATION_SPEC.md` as well.

---

**Next Recommended Action:**

Start with **Phase 1** (Pagination + Smart Transfer with warning + slot choice). This gives the biggest immediate usability win and matches the latest requirements the user described.

---

*This document is meant to be the practical execution checklist so nothing gets lost.*