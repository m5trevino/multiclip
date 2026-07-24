# Product Requirements Document — MultiClip V3

**Project:** MultiClip (MX Linux Clipboard Workstation)  
**Version:** 3.0  
**Date:** 2026-05-26  
**Status:** Ready for Implementation  
**Owner:** Flintx + AI Assistant  

---

> **Discovery Note:** Phase 1 Discovery and Phase 2 Analysis were completed via exhaustive review of existing finalized project specifications, including `multiclip-v3-spec.md`, `CLIPMAN_INTEGRATION_SPEC.md`, `MULTICLIP_CLIPMAN_IMPLEMENTATION_PLAN.md`, `00-EXECUTIVE_OVERVIEW.md`, and the four-stage analysis documents (Spark, Falcon, Eagle, Hawk). No knowledge gaps remain; all requirements below are grounded in documented ground truth.

---

## 1. Executive Summary

### Problem Statement
MultiClip V2 stabilized a minimal 30-slot clipboard manager with reliable root-boot hotkeys, but it remains an isolated scratchpad. Users cannot browse, curate, or sequence content from the system's live XFCE Clipman history (`~/.cache/xfce4/clipman/textsrc`). Additionally, critical UX gaps exist: the Orderly mode is non-functional, boot duplicates the application, there is no visual feedback on transfers, and users lack a quick way to compare text diffs without leaving the tool.

### Proposed Solution
MultiClip V3 transforms the application into a clipboard curation and sequencing workstation. It adds a paginated, live-refreshing Clipman History browser; fully wires the Orderly mode with FIFO/LIFO auto-capture; introduces smart "1 slot per line" transfer with manual slot selection; adds persistent Snippets with one-click removal; implements a visual flash + toast feedback system; integrates a Diff-Marker mode for side-by-side text comparison; and eliminates all boot-time duplication via single-instance guards and corrected init.d symlinks.

### Success Criteria
1. **Boot Reliability:** Exactly one MultiClip instance launches at system boot; zero duplicate processes measured via `ps aux | grep multiclip`.
2. **History Performance:** Clipman History panel renders any page of 50 items in < 100 ms on the target hardware (MX Linux, ~5 MB `textsrc`).
3. **Transfer Accuracy:** 100% of user-selected Clipman entries transfer to the intended Workbench slot(s) without silent data loss.
4. **Orderly Functionality:** Orderly mode captures every `Ctrl+C` into the next available slot and pastes sequentially with 100% cursor accuracy (no skipped or duplicated slots).
5. **Feedback Latency:** Visual flash animation and status toast appear within 50 ms of any transfer operation.
6. **Snippet Persistence:** 100% of added/edited snippets survive an application restart and a full system reboot.
7. **Diff Performance:** Diff-Marker mode calculates and renders side-by-side comparisons for texts up to 10,000 lines in < 2 seconds and stays under 100 MB RAM.

---

## 2. User Experience & Functionality

### User Personas

| Persona | Role | Primary Need |
|---|---|---|
| **Power User (Primary)** | Developer / writer on MX Linux who lives in terminals and editors | Curate long Clipman histories into reusable sequences without touching the mouse |
| **Administrator** | Sysadmin who manages the machine and needs root-boot reliability | Trust that MultiClip starts once, works under root, and never blocks the paste path |
| **Analyst** | User who compares logs, configs, or code snippets frequently | Diff text quickly inside the same tool instead of opening external diff utilities |

### User Stories & Acceptance Criteria

#### Story 1: Boot & Single Instance
> **As an** Administrator, **I want** MultiClip to start exactly once at boot as root, **so that** I never have competing hotkey listeners or X11 auth failures.

**Acceptance Criteria:**
- A single-instance guard using `fcntl.flock` on `/tmp/multiclip.lock` prevents a second process from fully initializing.
- The init.d service copies the desktop user's `~/.Xauthority` to `/tmp/.Xauthority_multiclip` before launch so X11 operations succeed under root.
- All `/etc/rc{2,3,4,5}.d/` symlinks are `S03multiclip` (not `K01`).
- Conflicting systemd and XFCE autostart entries are removed.

#### Story 2: Browse Paginated Clipman History
> **As a** Power User, **I want** to browse my full Clipman history in pages of 50 items, **so that** I can find old clips without loading a 5 MB file into memory at once.

**Acceptance Criteria:**
- The Clipman History panel displays exactly 50 entries per page.
- Pagination controls (`◀ Prev`, `Page X/Y`, `Next ▶`) are visible below the list.
- Only the current page's widgets are rendered; navigation to a new page discards the previous page's widgets.
- The full history is parsed once at startup and cached in memory; pagination is a view-layer filter.
- The list shows the decoded preview (first non-empty line, max 80 chars) of each `ClipEntry`.

#### Story 3: Live Refresh of History
> **As a** Power User, **I want** the Clipman History panel to update automatically when I copy new text, **so that** I don't have to restart the app to see recent clips.

**Acceptance Criteria:**
- A `tk.after(3000)` loop polls `~/.cache/xfce4/clipman/textsrc`.
- The loop compares file `mtime` to the last known `mtime`; re-parse and redraw only when `mtime` changes.
- On redraw, the view resets to page 1 to surface the newest content.
- The refresh must not steal focus or interrupt an active selection in the Workbench.

#### Story 4: Transfer with "1 Slot Per Line"
> **As a** Power User, **I want** each selected Clipman line to occupy its own Workbench slot, **so that** I can build ordered sequences quickly.

**Acceptance Criteria:**
- A button labeled `1 slot per line` (renamed from `TRANSFER AS ONE SLOT`) initiates the transfer.
- **Auto-Sequential (default):** Each selected line fills the next available empty slot in ascending order (1 → 30).
- **Manual Slot Selection:** The user may click any Workbench slot to set the starting slot. The chosen slot highlights with a unique color. Lines fill sequentially from that slot upward.
- If all 30 slots are full, a modal dialog appears with two options: (a) type a specific slot number to overwrite, or (b) confirm overwrite of the oldest slot.
- The UI enforces that the starting slot is within 1–30.

#### Story 5: Transfer as "Block Bundle"
> **As a** Power User, **I want** to force an entire multi-line selection into a single Workbench slot, **so that** large blocks of text stay together.

**Acceptance Criteria:**
- A button labeled `Block Bundle` (renamed from `TRANSFER AS BATCH`) performs the transfer.
- All selected Clipman entries are concatenated with a newline separator and placed into exactly one Workbench slot.
- The same "slots full" warning and overwrite choice apply as in Story 4.

#### Story 6: Double-Click Preview Popup
> **As a** Power User, **I want** to double-click any Clipman entry to see its full text and optionally transfer it to a specific slot, **so that** I can inspect content before committing it.

**Acceptance Criteria:**
- Double-clicking a Listbox row opens a modal popup (`ClipmanPreviewPopup`).
- The popup contains a scrollable `Text` widget showing the full decoded content.
- A number input field (1–30) and a `Transfer` button allow direct transfer to a chosen slot without closing the popup first.
- For multi-select, the popup offers two modes:
  - **Single:** Prev/Next buttons page through selected items one by one with a counter label (`"Item 3 of 7"`).
  - **Show All:** All selected items stacked with visual dividers.
- The popup closes via: X button, Escape key, or click outside the popup (bound to parent window).

#### Story 7: Transfer to Snippets
> **As a** Power User, **I want** to send any Clipman entry to a persistent Snippet slot, **so that** frequently used text survives reboots.

**Acceptance Criteria:**
- A context-menu option or button labeled `"Send to Snippet"` is available for every Clipman entry.
- Snippets are stored in `snippets.json` in the project root.
- The Snippets panel (bottom-left, under the 30 Workbench slots) displays up to 8 persistent slots.
- Each snippet shows a preview and supports inline edit/save.
- Snippet content is loaded from `snippets.json` at startup and saved on every add/edit/delete.

#### Story 8: Remove Snippets with One Click
> **As a** Power User, **I want** a dedicated X button next to each snippet for one-click removal, **so that** I don't have to clear text and hit Save.

**Acceptance Criteria:**
- Each snippet row displays an X button.
- Clicking X immediately removes the snippet from the UI and from `snippets.json`.
- A confirmation dialog is **not** required (the action is easily reversible by re-adding).

#### Story 9: Visual Transfer Feedback
> **As a** Power User, **I want** clear visual confirmation when I transfer content, **so that** I know the operation succeeded.

**Acceptance Criteria:**
- On every transfer (to Workbench or Snippets), the destination slot performs a slow pulse animation (~2 seconds, gold or bright green background).
- The bottom status bar displays a toast: `"Transferred to Slot 07"` or `"Saved to Snippet S3"`.
- The toast automatically clears after 3 seconds or is replaced by the next message.
- The flash animation must not block the main thread.

#### Story 10: Orderly Mode — Auto-Capture & Sequential Paste
> **As a** Power User, **I want** Orderly mode to automatically capture every `Ctrl+C` into Workbench slots and let me paste them back in order, **so that** I can queue up dozens of clips without manually assigning slot numbers.

**Acceptance Criteria:**
- Selecting the `Orderly` radio button activates the mode.
- Every normal `Ctrl+C` copy is intercepted and stored in the next empty Workbench slot.
- Pressing `Ctrl+V` (or the existing paste hotkey) pastes from the Workbench in sequence.
- Two independent cursors are maintained:
  - **Copy cursor:** next empty slot to fill.
  - **Paste cursor:** next filled slot to paste from.
- Wrap-around: When all 30 slots are full, new copies overwrite from slot 1 (circular buffer). The oldest content is evicted.
- The "next paste slot" is always visually highlighted/lit in the Workbench.
- The status bar shows queue info: `"Queue: 12 items | Next: Slot 05"`.

#### Story 11: Orderly Sub-Modes (FIFO / LIFO)
> **As a** Power User, **I want** to choose between FIFO and LIFO paste order in Orderly mode, **so that** I can either replay clips chronologically or access the most recent first.

**Acceptance Criteria:**
- When Orderly mode is active, two buttons appear inside the Clipman History panel: `FIFO` and `LIFO`.
- `FIFO` (First In, First Out): Pastes in the order copied (slot 1, then 2, then 3...).
- `LIFO` (Last In, First Out): Pastes in reverse order (most recent slot first).
- The active sub-mode is visually highlighted with a unique color.
- Sub-mode selection persists while Orderly is active and resets to FIFO when Orderly is deactivated.

#### Story 12: Diff-Marker Mode
> **As an** Analyst, **I want** to compare two blocks of text side-by-side with visual diff highlighting, **so that** I can spot changes without leaving MultiClip.

**Acceptance Criteria:**
- A `Diff-Marker` radio button exists alongside `MultiClip`, `Orderly`, and `Snippers`.
- The Diff-Marker panel provides two text input panels (left and right) with Load-from-Slot and Paste buttons.
- Clicking `Compare` calculates the diff using Python's `difflib` and displays results with color-coded tags:
  - Equal: white background
  - Insert: `#d4edda` background, `#155724` foreground
  - Delete: `#f8d7da` background, `#721c24` foreground
  - Replace: `#fff3cd` background, `#856404` foreground
- Two view modes are supported: Side-by-Side and Unified.
- A `Save Result` button writes the diff output to a chosen Workbench slot.
- Text size limit: 1 MB per panel. Exceeding this shows a clear error dialog.
- Diff calculation for 10,000 lines completes in < 2 seconds.

### Non-Goals

The following items are explicitly out of scope for V3 to protect the timeline:

1. **Network/cloud sync** — No server-side storage or cross-device clipboard sharing.
2. **File-system diff** — Diff-Marker is text-only; no directory or file comparison.
3. **Full-text search across Clipman history** — Pagination and browsing only; no search/filter bar.
4. **Custom themes / UI skins** — The existing dark dense UI style is preserved.
5. **Hotkeys for new V3 features** — Only the existing LCtrl+LAlt and RCtrl+RAlt hotkeys are guaranteed in V3. Snippet and transfer hotkeys are reserved for a future release.
6. **AI-powered summarization or smart grouping** — No LLM or ML components.
7. **Undo/Redo system** — Users rely on Clipman history and re-transfer if they make a mistake.

---

## 3. AI System Requirements

**Not Applicable.** MultiClip V3 contains no artificial intelligence, machine learning, or large-language-model components. All logic is deterministic, rules-based, and executes locally using Python's standard library (`difflib`, `tkinter`, `json`, `fcntl`).

---

## 4. Technical Specifications

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MultiClip V3 Architecture                       │
├─────────────────────────────────────────────────────────────────────────┤
│  User Layer          │  tkinter UI (gui/main_window.py)                 │
│  ├─ Workbench (30 slots, dense grid)                                   │
│  ├─ Clipman History (paginated Listbox, live refresh)                  │
│  ├─ Snippets (bottom-left, 8 persistent slots)                         │
│  ├─ Preview Popup (ClipmanPreviewPopup)                                │
│  ├─ Edit Overlay (EditOverlay)                                         │
│  └─ Diff-Marker Panel (diff_marker/DiffInterface)                      │
├─────────────────────────────────────────────────────────────────────────┤
│  Core Logic Layer    │  multiclip.py (MultiClipV2 class)                │
│  ├─ Hotkey listener (pynput, background thread)                        │
│  ├─ Slot persistence (clipboard_dict.json)                             │
│  ├─ Orderly queue cursors (copy_cursor, paste_cursor)                  │
│  ├─ Single-instance guard (fcntl.flock)                                │
│  └─ Paste injection (xdotool preferred, pyautogui fallback)            │
├─────────────────────────────────────────────────────────────────────────┤
│  Data Layer          │  shared/clipman_parser.py                        │
│  ├─ ClipmanParser (state-machine for textsrc, escaped semicolons)      │
│  ├─ ClipEntry dataclass (decode, preview, word_count)                  │
│  └─ SnippetsManager (snippets.json CRUD)                               │
├─────────────────────────────────────────────────────────────────────────┤
│  Diff Engine         │  diff_marker/                                    │
│  ├─ DiffManager (difflib.SequenceMatcher wrapper)                      │
│  ├─ DiffInterface (two-panel input, color-coded result)                │
│  └─ DiffResult / DiffLine / DiffType dataclasses                       │
└─────────────────────────────────────────────────────────────────────────┘
```

**Data Flow — Typical Transfer:**
1. User selects 3 lines in Clipman History panel.
2. `gui/main_window.py` calls `multiclip.py` transfer handler with selected `ClipEntry` IDs.
3. `multiclip.py` decodes content via `ClipmanParser`, determines target slot(s) via next-empty-slot logic.
4. Slots are updated in-memory and flushed to `clipboard_dict.json`.
5. `gui/main_window.py` receives the callback, triggers the slow-pulse flash on affected slot widgets and posts the toast.

**Data Flow — Orderly Mode:**
1. User activates Orderly mode via toolbar radio button.
2. `multiclip.py` sets `orderly_active = True` and initializes `copy_cursor = 1`, `paste_cursor = 1`.
3. pynput listener detects `Ctrl+C`; instead of passing through silently, it captures the system clipboard and writes it to `slots[str(copy_cursor)]`.
4. `copy_cursor` increments modulo 30.
5. On `Ctrl+V`, `multiclip.py` reads `slots[str(paste_cursor)]`, injects it via `xdotool`, and increments `paste_cursor` modulo 30.
6. The Workbench UI highlights the slot at `paste_cursor` to indicate "next paste source."

### Integration Points

| System | Interface | Details |
|---|---|---|
| **XFCE Clipman** | `~/.cache/xfce4/clipman/textsrc` | Read-only except for the natural side-effect that pasting moves items to the top of Clipman history. Parser handles `[texts]\ntexts=` header and escaped semicolons (`\;`). |
| **X11 / Display** | `xdotool type`, `pyautogui` | Paste injection prefers `xdotool` (more reliable under root). `pyautogui` is a fallback. |
| **OS Boot** | SysVinit `/etc/init.d/multiclip` | Service runs as root. Copies desktop user's `~/.Xauthority` to `/tmp/.Xauthority_multiclip`. Symlinks in rc2–rc5 must be `S03`. |
| **Persistence** | `clipboard_dict.json` | 30-slot JSON. Schema: `{ "slots": { "0": { "content": "..." }, ... } }` or flat `{ "slot_1": "..." }` (backward compatible). |
| **Snippets** | `snippets.json` | Flat array or dict of 8 entries. Survives restart. |
| **Python Environment** | Python 3.11+ | Dependencies: `pynput`, `pyautogui`, `pyperclip`. No web frameworks, no npm, no external APIs. |

### Security & Privacy

- **Local-only processing:** All data (clipboard content, diffs, snippets) stays on the local machine. No network egress.
- **Root execution safety:** The application runs as root solely to own global hotkeys. It does not execute user-provided shell commands. Paste injection is limited to `xdotool type` with literal string content.
- **Input validation:**
  - Slot index must be an integer in [1, 30].
  - Snippet index must be in [1, 8].
  - Diff text size is capped at 1 MB per panel to prevent memory exhaustion.
- **File permissions:** `clipboard_dict.json` and `snippets.json` are written with restrictive permissions (`0o600`) where possible to prevent world-readable clipboard history.
- **X11 auth:** The init.d script copies the desktop user's `.Xauthority` to a root-owned temp path. No `xhost +` or permissive X11 ACLs are used.

---

## 5. Risks & Roadmap

### Phased Rollout

| Phase | Deliverable | Key Features | Exit Criteria |
|---|---|---|---|
| **MVP** | V3.0 Core | Boot fixes, single-instance guard, pagination, live refresh, button renames, 1 slot per line, Block Bundle, preview popup, transfer to snippets, snippet removal, visual feedback | All acceptance criteria for Stories 1–9 pass in AI-internal testing |
| **v1.1** | Orderly + Diff | Fully wired Orderly mode (FIFO/LIFO), Diff-Marker mode integration, snippet persistence stress-testing | Stories 10–12 pass; 48-hour stability test with no memory leaks |
| **v2.0** | Polish & Hotkeys | Hotkeys for snippets and direct transfer, search/filter in Clipman History, optional file-based diff export | User acceptance testing complete; Lighthouse-style accessibility audit of tkinter colors |

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **textsrc format mutation** | Medium | High — parser breaks, history panel goes blank | Parser is defensive: ignores unknown escape sequences, falls back to raw line if decoding fails. Monitor `textsrc` header on every parse. |
| **Root X11 auth expiry** | Low | High — UI cannot start under root | Init.d script re-copies `.Xauthority` on every service restart. Log explicit errors if `DISPLAY` or `XAUTHORITY` is missing. |
| **Orderly cursor desync** | Medium | High — wrong slot pasted, data loss perception | Cursors are persisted in-memory only (volatile by design). Add a "Reset Sequence" button. Log every cursor move to stdout for debugging. |
| **Memory bloat on large textsrc** | Low | Medium — OOM or UI freeze | Parse once at startup with a generator; keep only `preview` strings in memory for the full history. Full `decoded_content` is loaded on-demand for preview popups. |
| **tkinter main-thread blocking** | Medium | Medium — UI freezes during diff or flash | Diff calculation runs in a `threading.Thread`. Flash animation uses `tk.after()`, never `time.sleep()`. |
| **Hotkey conflict with XFCE / Clipman** | Medium | High — new hotkeys override system shortcuts | V3 adds **no new global hotkeys**. All new features are UI-only. Future hotkeys (v2.0) will be chosen from unused modifier combinations and tested under root. |

### Testing & Validation Strategy

**Unit Testing (must pass before handover):**
- `ClipmanParser.parse()` returns correct `ClipEntry` count for a synthetic 1,000-line `textsrc`.
- `DiffManager.calculate_diff()` raises `ValueError` for text > 1 MB.
- `DiffManager.calculate_diff()` completes for 10,000 lines in < 2,000 ms (measured with `time.perf_counter`).
- Next-empty-slot logic returns slot 1 when all slots are empty, and slot 30 when slots 1–29 are full.
- Circular buffer wrap-around: copying to slot 30, then copying again writes to slot 1.

**Integration Testing (must pass before handover):**
- App launches cleanly with old dense UI (`gui/main_window.py`).
- Clipman History shows real data from the user's `textsrc`.
- Pagination navigates forward and backward without widget leaks.
- Live refresh detects a new `textsrc` write within 4 seconds.
- Transfer 1 item, 3 items, and 10 items to Workbench; verify slot contents match decoded source.
- "Slots full" warning appears when all 30 slots are occupied and user attempts transfer.
- Snippets add, edit, delete, and survive an application restart.
- Diff-Marker mode switches correctly, compares two texts, and saves the result to a Workbench slot.

**End-to-End Testing (user validation):**
- Boot the machine; verify exactly one `multiclip.py` process exists.
- Use existing hotkeys (LCtrl+LAlt + 1-0, RCtrl+RAlt + 1-0) for 5 minutes without failure.
- Activate Orderly mode; copy 10 items; paste them in FIFO and LIFO order; verify sequence accuracy.

---

*End of Product Requirements Document*
