# MultiClip V3 — Complete Specification

**Date:** 2026-05-26
**Project:** `/home/flintx/multiclip`
**Status:** Spec Finalized — Ready for Implementation

---

## Table of Contents

1. [Boot & Service Fixes](#1-boot--service-fixes)
2. [Clipman History Panel](#2-clipman-history-panel)
3. [Button Renames](#3-button-renames)
4. ["1 Slot Per Line" Mode](#4-1-slot-per-line-mode)
5. [Double-Click Preview Popup](#5-double-click-preview-popup)
6. [Transfer to Snippets](#6-transfer-to-snippets)
7. [Visual Transfer Feedback](#7-visual-transfer-feedback)
8. [Orderly Mode (Fully Wired)](#8-orderly-mode-fully-wired)
9. [Snippet Removal](#9-snippet-removal)
10. [Files to Modify](#10-files-to-modify)

---

## 1. Boot & Service Fixes

### Problem
- MultiClip opened **2 instances** at boot.
- Three conflicting startup mechanisms: systemd service, SysVinit service, and XFCE autostart.
- No single-instance guard in Python.
- Service ran as root but X11 auth failed (`Invalid MIT-MAGIC-COOKIE-1 key`).
- Init.d runlevel symlinks were `K01` (kill) instead of `S03` (start).

### Fixes Applied

| Fix | File | Detail |
|---|---|---|
| Remove systemd service | `/etc/systemd/system/multiclip.service` | Deleted via `fix-boot-duplication.sh` |
| Remove XFCE autostart | `~/.config/autostart/MultiClip V2.desktop` | Deleted via `fix-boot-duplication.sh` |
| Run as root with X11 cookie copy | `/etc/init.d/multiclip` | Copies `~/.Xauthority` to `/tmp/.Xauthority_multiclip` before launch |
| Single-instance guard | `multiclip.py` | `fcntl.flock` on `/tmp/multiclip.lock` |
| Fix symlinks | `/etc/rc2.d` through `/etc/rc5.d` | Changed from `K01multiclip` to `S03multiclip` |
| Live refresh | `gui/main_window.py` + `multiclip.py` | Polls `textsrc` every 3s via `tk.after()`, only redraws on mtime change |
| Pagination | `gui/main_window.py` | 50 items per page, only renders current page widgets |

### Commands to Apply

```bash
# Fix boot symlinks (run once)
sudo rm -f /etc/rc2.d/K01multiclip /etc/rc3.d/K01multiclip /etc/rc4.d/K01multiclip /etc/rc5.d/K01multiclip
sudo ln -s ../init.d/multiclip /etc/rc2.d/S03multiclip
sudo ln -s ../init.d/multiclip /etc/rc3.d/S03multiclip
sudo ln -s ../init.d/multiclip /etc/rc4.d/S03multiclip
sudo ln -s ../init.d/multiclip /etc/rc5.d/S03multiclip

# Remove duplicate startup mechanisms
sudo bash /home/flintx/multiclip/fix-boot-duplication.sh

# Restart service
sudo /etc/init.d/multiclip restart
```

---

## 2. Clipman History Panel

### Pagination
- **50 items per page**.
- **Controls**: `◀ Prev` | `Page X/Y` | `Next ▶` below the listbox.
- Only the current page's 50 items are rendered into the Listbox.
- Full history is parsed once at startup (all entries, not capped at 80).

### Live Refresh
- A `tk.after(3000)` loop polls `~/.cache/xfce4/clipman/textsrc`.
- Compares file `mtime` to avoid unnecessary redraws.
- On change: re-parses full history and resets to page 1.

---

## 3. Button Renames

| Old Label | New Label |
|---|---|
| `TRANSFER AS BATCH` | `Block Bundle` |
| `TRANSFER AS ONE SLOT` | `1 slot per line` |

---

## 4. "1 Slot Per Line" Mode

When the user clicks `1 slot per line`, each selected line from Clipman History gets its own Workbench slot.

### 4.1 Auto-Sequential (Default)
- Each line fills the **next available empty slot** in sequence.
- If all 30 slots are full, show the existing `"SLOTS FULL"` dialog.

### 4.2 Manual (Slot Selection)
- User **clicks a Workbench slot** to set the starting slot.
- The selected slot highlights with the same **unique color** as the `Sequential` toolbar toggle.
- Lines fill starting from that slot, going upward sequentially.
- If no slot is clicked, default to **slot 1**.
- The highlight makes it obvious which slot was chosen.

### 4.3 Mode Toggle
- A small toggle (dropdown or buttons) near the `1 slot per line` button lets the user switch between:
  - **Auto-Sequential**
  - **Manual Slot Selection**

---

## 5. Double-Click Preview Popup

When a user **double-clicks** a line in the Clipman History panel:

### Popup Contents
- **View**: Full text of the selected item(s) in a scrollable Text widget.
- **Transfer**: A number input field (1–30) + a **`Transfer` button**.
- Both options exist in the **same popup** — no need to close and reopen.

### Navigation (for multi-select)
- **Single** mode: Prev/Next buttons to page through selected items one by one.
- **Show All** mode: All selected items stacked with dividers.
- Counter label: `"Item 3 of 7"`.

### Close Behavior
- **X button** in top-right corner.
- **Escape key**.
- **Click outside** the popup (bound to parent window).

---

## 6. Transfer to Snippets

- Any item from Clipman History can be transferred to the **Snippets panel** (bottom-left, 8 persistent slots).
- Snippets are stored in `snippets.json` and survive restarts.
- Use case: "I use this text a lot — park it in snippets for now."
- Add a button or context-menu option: `"Send to Snippet"`.

---

## 7. Visual Transfer Feedback

When any transfer happens (to Workbench or Snippets):

### Flash Animation
- The destination slot does a **slow pulse** (not rapid blink).
- Style: `"1 long beeeeeeeeeeeeeep"` — gold or bright green background.
- Duration: ~2 seconds.
- The slot background flashes on/off slowly.

### Toast / Status
- Bottom status bar shows: `"Transferred to Slot 07"` or `"Saved to Snippet S3"`.
- Reuses the existing toast notification system.

---

## 8. Orderly Mode (Fully Wired)

The existing `Orderly` radio button in the toolbar is currently a no-op. It must be fully implemented.

### 8.1 Behavior

When `Orderly` mode is selected:

1. Every **normal Ctrl+C** copy is automatically captured into the Workbench slots.
2. Pressing **Ctrl+V** (or the existing paste hotkey) pastes from the Workbench in sequence.
3. **Independent cursors**:
   - **Copy cursor**: next empty slot to fill.
   - **Paste cursor**: next filled slot to paste from.
   - Example: copied 1–60, pasted 60–67, then copied 70–80 → next Ctrl+V pastes slot 68.
4. **Wrap around**: When all 30 slots fill, overwrite from slot 1 (circular buffer).

### 8.2 Sub-Modes

Two buttons appear **inside the Clipman History panel** when Orderly mode is active:

| Button | Behavior | Example (copied 50→60 in order) |
|---|---|---|
| **FIFO** (First In, First Out) | Paste in the order copied | Paste 50, then 51, then 52... |
| **LIFO** (Last In, First Out) | Paste in reverse order | Paste 60, then 59, then 58... |

- Buttons have **unique colors** so they're visually distinct.
- The active sub-mode is visually highlighted.

### 8.3 UI Integration

- The `Orderly` radio button in the toolbar activates/deactivates the mode.
- When active, FIFO/LIFO buttons appear in the Clipman History panel.
- The **"next paste slot"** is always **highlighted/lit up** in the Workbench so the user knows where the next paste will come from.
- Status bar shows queue info (e.g., `"Queue: 12 items | Next: Slot 05"`).

---

## 9. Snippet Removal

Two ways to remove a snippet:

1. **Clear text + hit Save** (current behavior).
2. **Dedicated X button** next to each snippet entry for one-click removal.

---

## 10. Files to Modify

| File | Changes |
|---|---|
| `multiclip.py` | Orderly queue logic, FIFO/LIFO cursors, auto-capture on Ctrl+C, wrap-around, slot highlighting |
| `gui/main_window.py` | Button renames, pagination, preview popup, transfer-to-snippets, flash animation, Orderly UI buttons, snippet X buttons, manual slot selection highlight |
| `shared/clipman_parser.py` | No changes needed (already reads full history) |
| `multiclip-init.d` | Already fixed (root + X11 cookie copy) |
| `multiclip-launcher.sh` | Already fixed (uses `/tmp/.Xauthority_multiclip`) |

---

*End of Specification*
