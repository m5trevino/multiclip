# MultiClip + Clipman Integration - Full Implementation Plan

**Project:** MultiClip (MX Linux)  
**Version:** 1.0  
**Date:** 2026-05-21  
**Status:** Ready for execution  
**Owner:** User (Flintx) + AI Assistant

## Guiding Rules (Non-Negotiable)

1. **No hallucination.** If anything is unclear, stop and ask. Do it right, even if it takes longer.
2. **Protect the working core.** The current LCtrl+LAlt / RCtrl+RAlt hotkeys and paste logic must remain reliable.
3. **Keep it practical.** This is a tool to help the user work faster on other projects, not a big architecture project.
4. **Test before handover.** All logic must be internally tested by the AI before handing over to the user for hotkey testing.
5. **Use the existing old dense UI** as the base (the one the user likes).

---

## Current State (What Already Works)

- Old dense 30-slot UI from `gui/main_window.py` loads via `multiclip.py`
- Basic Clipman History Listbox exists on the right side
- Basic transfer of whole selected rows to OG slots (simple version)
- Working hotkeys for classic copy/paste into OG slots
- Improved parser that can read the real textsrc file
- Spec document exists (`CLIPMAN_INTEGRATION_SPEC.md`)

---

## High-Level Goals

- Full pagination in the Clipman History panel (right side)
- Proper "Lock Selection" + "Transfer as Batch / One Slot" controls
- Smart transfer logic that matches all examples the user has shown (with warnings when slots are full)
- Snippets area in the bottom-left (under the 30 OG slots), fully persistent
- All logic internally tested before user receives it
- User will only test hotkeys at the end

---

## Detailed Phased Implementation Plan

### Phase 1: UI Layout & New Controls (Right Side + Bottom Left)

**Goal:** Get the visual layout the user wants and the new buttons in place.

**Tasks:**

1.1 **Add "Lock Selection" button** in the Clipman History panel (right side)
   - Button text: "LOCK SELECTION"
   - When clicked, it commits the current multi-selection in the listbox as a "locked group"
   - User can then make new selections for the next group
   - Show some visual indication of locked groups (e.g. different color or "(Locked)" text)

1.2 **Add "Transfer as Batch" button** in the Clipman History panel
   - Button text: "TRANSFER AS BATCH"
   - This will be the main transfer button that respects the user's groupings (locked selections + individual selections)

1.3 **Add "Transfer as One Slot" button** (optional but requested)
   - For cases where the user wants to force a large highlighted block into a single OG slot

1.4 **Add Snippets section in the bottom-left**
   - Location: Directly underneath the 30 OG slots (bottom left area)
   - Simple list or grid of snippets
   - Buttons: Add, Edit, Delete, Save
   - Persistent storage (JSON file in the project folder)
   - User can start adding snippets immediately

1.5 **Clean up the right panel layout**
   - Decide final stacking order of:
     - Clipman History (with new buttons)
     - Old Snippet Vault (keep or hide for now?)
   - Make sure the layout doesn't look cramped

**Acceptance Criteria:**
- The window opens cleanly with the old dense layout.
- Clipman History panel has Lock + Transfer as Batch buttons.
- Snippets area exists in bottom-left and can add/edit/save snippets that persist after restart.

---

### Phase 2: Lock / Commit Logic (Right Side)

**Goal:** Allow the user to build multiple groups before transferring.

**Tasks:**

2.1 Implement "Lock Selection" behavior
   - Store locked groups separately from current selection
   - Visual feedback in the listbox (e.g. green text or tag for locked items)

2.2 Allow multiple locks
   - User can lock several groups before hitting Transfer

2.3 On Transfer, respect the locked groups + any remaining selected items

---

### Phase 3: Transfer Logic - "Lock it down" (Core Logic)

**Goal:** Make the transfer behavior match exactly what the user has described across all examples and images.

**Rules to implement (synthesized from conversation):**

3.1 Basic Transfer (when using "Transfer as Batch")
   - Each selected Clipman item (row) becomes **one OG slot**
   - Order = the order the user selected the rows in the listbox

3.2 When user has used "Lock Selection"
   - Each locked group is treated as one or more slots depending on whether the user wants splitting inside the group
   - For now (first version): Treat each locked group as **one slot** (whole content of the selected rows in that group)

3.3 "Transfer as One Slot" path
   - Force the entire current selection (even multi-line) into **exactly one** OG slot

3.4 Full OG Slots Handling (Critical)
   - If there are empty OG slots → fill the next empty ones first (in order)
   - If no empty slots remain:
     - Show a clear warning dialog
     - Options for the user:
       - Type a specific slot number to overwrite
       - Or confirm "Overwrite the oldest slot"
   - Never silently fail or crash

3.5 Testing Requirements (must pass before handover)
   - Single item transfer → goes to next empty slot (or chosen slot)
   - Multiple items transfer → each gets its own slot in selection order
   - Transfer when slots are full → warning appears + user can choose slot
   - "Transfer as One Slot" forces everything into one slot
   - Lock + multiple groups works correctly

---

### Phase 4: Snippets Area (Bottom Left)

**Tasks:**

4.1 Create the UI section under the 30 OG slots
4.2 Add Add / Edit / Delete / Save functionality
4.3 Persistent storage (save to `snippets.json` or similar in the project root)
4.4 Make sure snippets survive app restart
4.5 Basic testing: add, edit, delete, restart app, verify they are still there

---

### Phase 5: Internal Testing (Before Handover)

The AI must test the following before giving the code to the user:

- [ ] App launches cleanly with the updated UI
- [ ] Clipman History shows real data from the user's textsrc
- [ ] Pagination works (if implemented in this plan)
- [ ] Lock Selection works (multiple locks)
- [ ] Transfer as Batch works for 1 item, 2 items, 3+ items
- [ ] Transfer as One Slot works
- [ ] When OG slots are full, warning + slot choice works
- [ ] Snippets can be added, edited, deleted, and survive restart
- [ ] No crashes or broken behavior in normal use

Only after all of the above pass should the code be handed over.

---

### Phase 6: User Testing (Hotkeys)

After the AI hands over a tested build, the user will:

- Test all functionality with the actual hotkeys (LCtrl+Alt and RCtrl+Alt)
- Test sequential and batch modes
- Test snippet hotkeys (once defined)
- Give final feedback

---

## Open Decisions / Questions (to be answered during implementation)

- Exact button names and wording for warnings
- How to visually show "locked" items in the listbox
- Whether to keep the old "Snippet Vault" on the right or fully replace it with the new bottom-left Snippets
- How many snippets should be shown at once (fixed number vs scrollable)
- Exact hotkeys for new features (user will decide later)

---

## File Locations (Reference)

- Main logic: `multiclip.py`
- Old dense UI: `gui/main_window.py`
- Parser: `shared/clipman_parser.py`
- Spec: `docs/CLIPMAN_INTEGRATION_SPEC.md`
- This Plan: `docs/MULTICLIP_CLIPMAN_IMPLEMENTATION_PLAN.md`

---

**This document is the master execution checklist.**

Nothing should be considered "done" until it is:
1. Implemented
2. Tested by the AI
3. Documented in this plan (checkbox ticked)

The user will only receive the final build after Phase 5 is complete.