# MultiClip + Clipman Integration: UI Layout & Transfer Logic

**Status:** Current working understanding (as of 2026-05-21)  
**Goal:** Keep the classic MultiClip experience while adding powerful Clipman history support without overcomplicating the tool.

---

## Overall Layout (What You Want)

The UI is based on the old dense "Industrial" 30-slot workbench that you like.

- **Left / Main Area**: The classic **30 OG Slots** (Workbench)
  - This is your primary working area.
  - This is where you do manual reordering.
  - This is where **Sequence mode** and **Batch mode** operate.
  - You can reset the order back to 1–30 at any time.

- **Right Area (or available space)**: **CLIPMAN HISTORY** panel
  - This is the new addition.
  - It shows recent entries from your real `~/.cache/xfce4/clipman/textsrc` file.
  - This area is **only a source** — it feeds the OG slots.
  - You do **not** run sequencing or batch directly from this panel.

---

## Current Implementation (Listbox Version)

The Clipman History panel is currently implemented as a **Listbox**.

- Each row = one full Clipman history entry (shown as its preview).
- You can multi-select rows (`Ctrl+click` or `Shift+click`).
- Selection order matters.

### Transfer Behavior (Current Rule)

When you select one or more rows in the Clipman History list and click **"TRANSFER SELECTED TO OG SLOTS"**:

- Each selected row becomes **exactly one OG slot**.
- Slots are filled **in the exact order you selected the rows**.
- If there are empty slots, it prefers filling empty ones first.
- If no empty slots remain, it starts overwriting from the beginning.

**Examples:**

1. You select 3 separate Clipman history items → They go into 3 separate OG slots (in the order you clicked them).
2. You select one long Clipman entry that contains multiple logical blocks → Currently it goes in as **one slot** (because it's one row in the listbox).

---

## Your Refined Vision (From Recent Examples)

You want more granular control over grouping when transferring:

- **Simple case** (current Listbox strength):  
  Selecting multiple whole rows → each row becomes its own slot. This is clean and easy.

- **Advanced case** (what you want to support):  
  Inside one long Clipman history entry, if you select multiple separate sections (e.g. two different command blocks), those sections should land in **separate OG slots**, not smashed together.

You also mentioned wanting a future "lock / commit" mechanism so you can:
- Select some text/lines → lock them as one group.
- Then select more → decide whether they become new separate slots or get added to the previous group.

---

## Current vs Desired Transfer Rules

| Scenario                              | Current Behavior (Listbox)      | Desired Behavior                          |
|---------------------------------------|----------------------------------|-------------------------------------------|
| Select 3 different history items      | 3 slots (in selection order)    | 3 slots (in selection order)             |
| Select multiple lines inside **one** long entry | 1 slot (whole entry)           | Multiple slots (one per logical block)   |
| Mixed selection across items + inside items | Not supported yet               | Respect natural separations + user intent |
| Reordering after transfer             | Manual in OG slots              | Manual in OG slots + Reset button        |

---

## Sequence & Batch Rules

- **Sequence mode** and **Batch mode** only work on the **OG 30 slots**.
- Clipman history is **never** the direct source for sequencing or batching.
- After you transfer items into the OG slots, you can:
  - Manually reorder them
  - Hit a **Reset / Normalize** button to restore default 1–30 order
  - Then run your normal sequence or batch hotkeys from the OG area

---

## Why the Current Listbox Approach Has Value

- Very clean and scannable list of distinct history items.
- Easy multi-select with preserved order.
- Lightweight and fast.
- Good for the common "I want these whole pastes in this order" workflow.
- Matches the simple, non-wasteful aesthetic you like.

We can evolve the right panel later (e.g. show lines instead of whole entries, or add a detail view for intra-entry selection) if the current row-based selection becomes limiting.

---

## Next Steps (Practical Path)

1. **Parser** — Keep improving so it reliably gives clean, usable entries (and can eventually support line-level splitting when needed).
2. **Transfer Logic** — Make the button respect the rules above (whole items for now, with hooks for future splitting).
3. **UI Polish** — Keep the old dense layout as the base. Add the Clipman panel in the available space you showed.
4. **Hotkeys** — You will define these later once the logic feels right.
5. **Testing** — Use real data from your textsrc and iterate based on actual use.

---

**Document Purpose**: This file captures the current agreed understanding so we don’t lose the details as we iterate. We can update it as the vision sharpens.

Let me know if you want any section expanded, clarified, or turned into a tighter spec for the next piece of work.