plan-format: 1

Implement the MultiClip V3 feature set on top of the stable V2 rehab core: Clipman History pagination, button renames, "1 slot per line" transfer mode (auto-sequential + manual slot selection), fully wired Orderly mode (FIFO/LIFO, auto-capture, independent cursors), Transfer-to-Snippets, snippet X-button removal, visual transfer flash feedback, and preview-popup transfer — while preserving the existing reliable LCtrl+LAlt / RCtrl+RAlt hotkeys and root-boot stability.

- Sub-agents: read `docs/CLIPMAN_INTEGRATION_SPEC.md` and `multiclip-v3-spec.md` before starting work
- Model tiers — each step's **Agent** field specifies the required model tier. Map to your provider's models:
  - `strongest` = most capable model available (e.g., Opus). Use for architecture, review, risk assessment.
  - `default` = standard model (e.g., Sonnet). Use for implementation, testing, standard tasks.
  - When spawning sub-agents, select the model matching this tier.
- Protect the working core: the LCtrl+LAlt copy and RCtrl+RAlt paste paths in `multiclip.py` must not be altered except to add Orderly-mode hooks. The `xdotool`-first paste injection is sacred.
- The project runs as root on MX Linux (XFCE + SysVinit). Any new init/service changes must follow the existing `/etc/init.d/multiclip` pattern.
- All changes are local Python/tkinter. No network, no external APIs, no new dependencies beyond the existing `pyperclip`, `pynput`, `pyautogui`, `tkinter` stack.
- UI must remain usable at 1100x850 (the current `gui/main_window.py` geometry).
- `clipboard_dict.json` and `snippets.json` are the only persisted data files. No SQLite, no new file formats.
- One session per step preferred — each step produces a runnable, testable increment.
- Design Decision #1: Button renames happen first (Step 01) because every subsequent step's documentation, tests, and UI copy reference the new names. Old names create confusion in a multi-agent pipeline.
- Design Decision #2: Orderly mode is split into core logic (Step 03) and UI wiring (Step 04). Rationale: the core logic touches the hotkey path (risky) and must be verified in isolation before adding UI chrome. The UI step is safer and can be reverted independently.
- Design Decision #3: Transfer-to-Snippets and Snippet Removal are bundled (Step 05). Rationale: both touch the same `snippets.json` file and the same bottom-left Snippets panel widgets. Doing them separately would cause merge conflicts on `gui/main_window.py` lines 374-391.
- Design Decision #4: Visual Transfer Feedback (Step 06) is deferred until after all transfer paths exist. Rationale: flash animation must instrument every transfer call site; it's cheaper to instrument them once they're all stable.
- No CI server exists. Verification is local: launch the app, perform the action, verify behavior, record result in Progress Log.
- Hotkey testing is reserved for the user (Phase 8) because root + X11 hotkeys cannot be reliably automated in a headless environment. The AI verifies logic paths via unit-like checks and UI state inspection.
- Rollback strategy: each step notes the specific files changed. If a step fails catastrophically, restore those files from git or from backup copies created at step start.
- Plan mutation protocol: if >50% of remaining steps are affected by a scope change, pause and ask the user whether to mutate this plan or create a new one.

Operations are classified by reversibility. Executing agents must respect these boundaries.

Autonomous (execute without asking):
- Python file edits, local JSON data edits, running the app locally for visual verification, creating backup copies of files before editing.

User-confirmed (ask before executing):
- Modifying `/etc/init.d/` or system rc.d symlinks, deleting `clipboard_dict.json` or `snippets.json`, `sudo` operations outside the project directory.

Not all plan content carries the same level of constraint. Executing agents must respect these tiers:

- Zero freedom (exact commands, no deviation): hotkey modifier constants (`ctrl_l`, `ctrl_r`, `alt_l`, `alt_r`), paste injection method (`xdotool` preferred), file paths (`clipboard_dict.json`, `snippets.json`), slot count (30), snippet count (8).
- Low freedom (approach specified, implementation flexible): widget layout within the existing left/right panel structure, animation timing (+/-0.5s), dialog wording, color choices for highlights.
- High freedom (goal only): internal helper method names, comment prose, exact tkinter styling constants (as long as the look is consistent).


---

Branch: multiclip-step-01-button-renames-and-toggle
Size: S
Isolation: main-tree
Agent: default
Context (cold-start brief):
The MultiClip project is a Python tkinter app for MX Linux. The current working UI is in `gui/main_window.py` (dense 30-slot workbench + Clipman History panel on the right + Snippets bottom-left). The V3 spec requires two button renames in the Clipman History panel and a mode toggle for the "1 slot per line" feature. This step is pure UI label/widget changes — zero logic risk. The existing transfer callbacks (`_on_clipman_transfer_batch`, `_on_clipman_transfer_one_slot`) remain functionally unchanged; only their triggering buttons are renamed and a toggle is added.

See Design Decision #1 for why renames happen first.

Tasks:
- [exact] In `gui/main_window.py`, locate the `batch_btn` (line ~472). Change its text from `"TRANSFER AS BATCH"` to `"Block Bundle"`.
- [exact] In `gui/main_window.py`, locate the `one_slot_btn` (line ~477). Change its text from `"TRANSFER AS ONE SLOT"` to `"1 slot per line"`.
- [guided] Add a small toggle widget (ttk.Combobox or two small ttk.Radiobuttons) directly underneath the `"1 slot per line"` button in the Clipman History panel. Label it `"Mode:"` with two options: `"Auto-Sequential"` and `"Manual Slot"`. Store the selected value in a `tk.StringVar` named `self.slot_mode_var` with default `"Auto-Sequential"`. This toggle controls the behavior of the "1 slot per line" transfer path (implemented in Step 02).
- [exact] Update the `_on_clipman_transfer_one_slot` method name to `_on_transfer_one_slot_per_line` to match the new button label. Update the button's `command=` binding accordingly. Keep the old method as an alias (deprecated) for one step to avoid breaking any external callers.
- [exact] Verify the app still launches: `cd /home/flintx/multiclip && python3 -c "from gui.main_window import MainWindow; w=MainWindow(); print('UI loads OK'); w.destroy()"`

Rollback: `git checkout -- gui/main_window.py` (or restore from backup copy made at step start).

Verification:
- Automated: grep for `"TRANSFER AS BATCH"` in `gui/main_window.py` — returns 0 matches.
- Automated: grep for `"Block Bundle"` in `gui/main_window.py` — returns 1+ matches.
- Automated: grep for `"1 slot per line"` in `gui/main_window.py` — returns 1+ matches.
- Manual: Launch the app. Visually confirm the Clipman History panel shows "Block Bundle", "1 slot per line", and the Mode toggle beneath it.

Exit criteria: Button texts match V3 spec. Mode toggle widget exists and defaults to "Auto-Sequential". App launches without error. No functional behavior has changed yet.


---

Branch: multiclip-step-02-one-slot-per-line-logic
Size: M
Isolation: main-tree
Agent: default
Context (cold-start brief):
The MultiClip V3 spec defines "1 slot per line" as a transfer mode where each selected line from Clipman History gets its own Workbench slot. Two sub-modes exist:
1. **Auto-Sequential** (default): fills the next available empty slot in order 1-30.
2. **Manual Slot Selection**: user clicks a Workbench slot to set the starting slot; lines fill upward sequentially from there. The chosen slot gets a temporary highlight.

The existing transfer logic lives in `multiclip.py` (`_transfer_clipman_to_og_slots`) and `gui/main_window.py` (`_on_clipman_transfer_batch`, `_on_transfer_one_slot_per_line`). The "1 slot per line" button currently joins all selected items into one string. It must be changed to split each selected item into its own slot.

When all 30 slots are full, the existing warning dialog (already in `multiclip.py`) must appear. That dialog already supports user-choosing a target slot or falling back to slot 1.

Key files: `multiclip.py`, `gui/main_window.py`.

Tasks:
- [guided] In `gui/main_window.py`, create a method `_get_transfer_mode() -> str` that returns `"auto"` or `"manual"` based on the `slot_mode_var` toggle added in Step 01.
- [guided] In `gui/main_window.py`, add a `_manual_start_slot: Optional[int] = None` instance variable. When the user clicks a Workbench slot preview label while `"Manual Slot"` mode is active, set `_manual_start_slot` to that slot_id and visually highlight the slot (e.g., temporary gold background on the SlotDisplay container). Clicking another slot moves the highlight. Clicking the same slot clears it.
- [guided] In `multiclip.py`, refactor `_transfer_clipman_to_og_slots` to accept an optional `start_slot: int = None` parameter:
  - If `start_slot` is None: use existing "next empty slot" logic.
  - If `start_slot` is provided: fill starting from that slot number, wrapping around 30->1 if needed.
  - The "slots full" warning dialog behavior remains unchanged.
- [guided] In `gui/main_window.py`, rewrite `_on_transfer_one_slot_per_line`:
  - If mode is `"Auto-Sequential"`: call the refactored transfer with `start_slot=None`.
  - If mode is `"Manual Slot"` and `_manual_start_slot` is set: call transfer with `start_slot=_manual_start_slot`.
  - If mode is `"Manual Slot"` but no slot was clicked: show a brief status message `"Click a Workbench slot first"` and return.
- [exact] Update `multiclip.py` to pass the `start_slot` parameter through to the slot-filling loop. Ensure the wrap-around logic (`slot = ((slot - 1) % 30) + 1`) is applied when `start_slot` is provided.
- [exact] Run a logic-only test (no UI): `python3 -c "from multiclip import MultiClipV2; m=object.__new__(MultiClipV2); m.slots={str(i):'' for i in range(1,31)}; m.slots['5']='existing'; print(m.slots)"` — verify the object can be instantiated for testing. (Note: full instantiation requires X11; use `object.__new__` for pure logic tests.)

Rollback: `git checkout -- multiclip.py gui/main_window.py`

Verification:
- Automated: `python3 -c "
import sys
sys.path.insert(0, '/home/flintx/multiclip')
from multiclip import MultiClipV2
m = object.__new__(MultiClipV2)
m.slots = {str(i): '' for i in range(1, 31)}
m.slots['1'] = 'a'
m.slots['2'] = 'b'
empty = [i for i in range(1, 31) if not m.slots[str(i)]]
print('Next empty:', empty[0] if empty else 'FULL')
"` — outputs "Next empty: 3".
- Manual: Launch app. Select 3 Clipman items. Click "1 slot per line" in Auto-Sequential mode. Verify 3 slots are filled starting from the first empty slot.
- Manual: Switch to Manual Slot mode. Click Workbench slot 10. Select 2 Clipman items. Click "1 slot per line". Verify slots 10 and 11 are filled.
- Manual: Fill all 30 slots. Attempt a transfer. Verify the "SLOTS FULL" dialog appears.

Exit criteria: "1 slot per line" splits selected items into individual slots. Auto-Sequential fills next empty slot. Manual fills from the clicked slot with wrap-around. Full-slot warning dialog still works. No regressions to "Block Bundle" (batch) transfer.


---

Branch: multiclip-step-03-orderly-mode-core
Size: M
Isolation: main-tree
Agent: strongest
Context (cold-start brief):
The MultiClip toolbar has an "Orderly" radio button that is currently a no-op. The V3 spec requires fully wired Orderly mode with these behaviors:
1. **Auto-capture**: every normal Ctrl+C (system clipboard copy) is automatically captured into the next empty Workbench slot.
2. **Sequential paste**: pressing Ctrl+V (or the existing paste hotkey) pastes from the Workbench in sequence.
3. **Independent cursors**: a copy cursor (next empty slot to fill) and a paste cursor (next filled slot to paste from) operate independently. Example: copied 1-60, pasted 60-67, then copied 70-80 -> next Ctrl+V pastes slot 68.
4. **Wrap-around**: when all 30 slots fill, overwrite from slot 1 (circular buffer).

The existing hotkey system in `multiclip.py` uses `pynput` to detect LCtrl+LAlt+number (copy to slot) and RCtrl+RAlt+number (paste from slot). Orderly mode must NOT interfere with these hotkeys. Instead, it hooks into the system clipboard: when Orderly is active, any clipboard change (detected via polling or `pyperclip` watch) triggers an auto-capture.

Because the app runs as root, clipboard monitoring must be lightweight and not spam X11. A 300ms polling loop checking `pyperclip.paste()` against a last-seen hash is acceptable.

The existing `_register_hotkeys` and `_handle_combo` methods must remain untouched except to add an Orderly-active flag check. The paste logic (`paste_from_slot`) can be reused by calling it with the paste cursor's slot number.

Key file: `multiclip.py`.

Tasks:
- [guided] In `multiclip.py`, add Orderly state variables to `__init__`:
  - `self.orderly_active = False`
  - `self.orderly_copy_cursor = 1`  # next slot to fill
  - `self.orderly_paste_cursor = 1` # next slot to paste from
  - `self.orderly_fifo = True`      # True=FIFO, False=LIFO
  - `self.orderly_last_clip_hash = ""`
- [guided] Add `start_orderly_monitor()` and `stop_orderly_monitor()` methods:
  - `start_orderly_monitor`: sets `orderly_active = True`, starts a `threading.Timer` loop (every 300ms) that calls `_orderly_clip_check()`.
  - `stop_orderly_monitor`: sets `orderly_active = False`, cancels the timer.
- [guided] Add `_orderly_clip_check()`:
  - Gets current clipboard via `pyperclip.paste()`.
  - Computes a simple hash (`hashlib.md5(content.encode()).hexdigest()` or `len+first50`).
  - If hash differs from `orderly_last_clip_hash` and content is non-empty and content is not one of the recently auto-captured items (to avoid self-feedback loop):
    - Store content in slot `str(orderly_copy_cursor)`.
    - Increment copy cursor: `orderly_copy_cursor = (orderly_copy_cursor % 30) + 1` (wrap 30->1).
    - Update `orderly_last_clip_hash`.
    - Save slots.
- [guided] Add `orderly_paste_next()`:
  - If FIFO: paste from `orderly_paste_cursor`, then increment with wrap.
  - If LIFO: paste from `(orderly_copy_cursor - 1)` (the most recently filled slot), but do NOT advance copy cursor. Instead track a separate LIFO read pointer, or compute dynamically: find the highest filled slot walking backward from `copy_cursor - 1`.
  - Simpler LIFO implementation: maintain `orderly_lifo_cursor` initialized to `copy_cursor - 1`. On each LIFO paste, decrement with wrap (30->1). When it meets `paste_cursor` underflow, wrap to 30.
  - Reuse the existing `paste_from_slot(slot_num)` method for actual injection.
- [guided] Hook the existing `paste_from_slot` or add a new path: when `orderly_active` is True and the user triggers a paste (RCtrl+RAlt+number is unchanged; for Orderly we may need a new hotkey or UI trigger — for now, expose `orderly_paste_next()` as a callable that the UI can bind later). Do NOT change the existing RCtrl+RAlt+number behavior.
- [exact] Ensure the clipboard monitor thread is daemonic and does not prevent clean exit. Register timer cancellation in the existing atexit/signal handlers.
- [exact] Add a safety check: if the new clipboard content matches the content of the slot about to be written (to prevent duplicate fills when the user copies the same text twice), skip the write.

Rollback: `git checkout -- multiclip.py`

Verification:
- Automated: `python3 -c "
import sys, hashlib
sys.path.insert(0, '/home/flintx/multiclip')
from multiclip import MultiClipV2
m = object.__new__(MultiClipV2)
m.slots = {str(i): '' for i in range(1, 31)}
m.orderly_copy_cursor = 1
m.orderly_paste_cursor = 1
m.orderly_fifo = True
content = 'hello'
m.slots[str(m.orderly_copy_cursor)] = content
m.orderly_copy_cursor = (m.orderly_copy_cursor % 30) + 1
print('Copy cursor:', m.orderly_copy_cursor)
print('Slot 1:', m.slots['1'])
"` — outputs Copy cursor: 2, Slot 1: hello.
- Manual: Launch app. Activate Orderly mode via UI (toolbar radio button). Copy text from another app with Ctrl+C. Verify the text appears in Slot 1. Copy again. Verify Slot 2 fills. Continue to slot 30. Copy once more. Verify Slot 1 overwrites (wrap-around).
- Manual: With items in slots 1-3, trigger orderly paste (via future UI button or debug call). Verify FIFO pastes 1, then 2, then 3.
- Manual: Switch to LIFO (UI not ready yet; test via debug). Verify pastes 3, then 2, then 1.

Exit criteria: Orderly auto-capture works. Copy cursor wraps 30->1. FIFO pastes in fill order. LIFO pastes in reverse fill order. Existing LCtrl+LAlt/RCtrl+RAlt hotkeys are unaffected. No crashes on exit.


---

Branch: multiclip-step-04-orderly-mode-ui
Size: M
Isolation: main-tree
Agent: default
Context (cold-start brief):
Step 03 implemented Orderly mode core logic in `multiclip.py` (auto-capture, FIFO/LIFO cursors, wrap-around). This step wires the UI:
1. The existing "Orderly" toolbar radio button must call `start_orderly_monitor()` / `stop_orderly_monitor()`.
2. When Orderly is active, two buttons (FIFO / LIFO) appear inside the Clipman History panel.
3. The "next paste slot" is highlighted in the Workbench.
4. The status bar shows queue info.

The existing `MainWindow._on_mode_change` and `_show_mode_panel` methods handle mode switching. The "Orderly" mode already has a panel (`orderly_panel`) but it is bare. We enhance that panel and also conditionally show FIFO/LIFO buttons inside the Clipman History panel.

Key file: `gui/main_window.py`.

Tasks:
- [guided] In `gui/main_window.py`, wire `_on_mode_change`:
  - When mode becomes "Orderly": call `multiclip_app.start_orderly_monitor()` (expose a callback or direct reference).
  - When mode leaves "Orderly": call `multiclip_app.stop_orderly_monitor()`.
- [guided] In the Clipman History panel (`clipman_panel`), add a sub-frame `orderly_controls_frame` that is visible only when Orderly is active. It contains two buttons:
  - `"FIFO"` (bg green when active)
  - `"LIFO"` (bg blue when active)
  - Clicking toggles `multiclip_app.orderly_fifo` and updates button colors.
- [guided] Add a method `highlight_orderly_slot(slot_num: int)` in `MainWindow` that temporarily sets the background of the corresponding `SlotDisplay` container to a bright color (e.g., `#ffd700` gold). Call this from the multiclip core after each paste to show the "next" slot. Clear previous highlight before setting new one.
- [guided] Update `MainWindow.update_bottom_status` to accept an optional queue info string. When Orderly is active, display `"Queue: N items | Next: Slot XX"`.
- [exact] Ensure the FIFO/LIFO buttons are destroyed/hidden when mode switches away from Orderly.
- [exact] Ensure the slot highlight is cleared when Orderly is deactivated.

Rollback: `git checkout -- gui/main_window.py`

Verification:
- Manual: Launch app. Click "Orderly" toolbar radio. Verify FIFO/LIFO buttons appear in Clipman panel. Click LIFO — button highlights blue, FIFO dims. Copy text externally. Verify slot fills. Watch the Workbench — the "next paste slot" should glow gold.
- Manual: Switch back to "Multiclip" mode. Verify FIFO/LIFO buttons disappear. Verify Orderly slot highlight clears.
- Manual: Status bar shows queue count and next slot number while Orderly is active.

Exit criteria: Orderly radio button starts/stops monitor. FIFO/LIFO buttons visible only in Orderly mode. Active sub-mode visually highlighted. Next-paste slot glows in Workbench. Status bar shows queue info. Mode switch away from Orderly cleans up all visual state.

---

Branch: multiclip-step-05-snippets-transfer-and-removal
Size: M
Isolation: main-tree
Agent: default
Context (cold-start brief):
The MultiClip V3 spec requires two Snippets enhancements:
1. **Transfer to Snippets**: any Clipman History item (or Workbench slot) can be sent to one of the 8 persistent Snippet slots (bottom-left).
2. **Snippet Removal**: a dedicated X button next to each snippet entry for one-click clearing.

The existing Snippets panel is in `gui/main_window.py` lines 374-391. It already has Save buttons and loads from `snippets.json`. The `shared/snippets_manager.py` (`SnippetVault`) handles persistence but is not currently wired into `MainWindow`. We can either wire `SnippetVault` or keep the existing direct JSON approach. Since the existing code already reads/writes `snippets.json` directly in `MainWindow._load_snippets` and `_save_snippet`, we extend that pattern to avoid introducing a new abstraction layer mid-flight.

Key files: `gui/main_window.py`, `multiclip.py` (for transfer callback).

Tasks:
- [guided] In `gui/main_window.py`, add a `"Send to Snippet"` button in the Clipman History panel button row (`btn_frame`). When clicked:
  - Get selected Clipman entries.
  - Open a small popup with 8 numbered buttons (S1-S8).
  - Clicking a number saves the selected content to that snippet index and persists to `snippets.json`.
  - If multiple entries selected, send each to consecutive snippet slots (wrapping 8->1).
- [guided] In `gui/main_window.py`, for each Snippet row (lines 379-390), add an `"X"` button to the right of the Save button. Clicking it:
  - Clears the Entry widget.
  - Removes the key from `snippets.json` (or sets to empty string).
  - Updates the JSON file immediately.
- [guided] Update `multiclip.py` to expose a `_send_to_snippets(selected_entries)` callback that can be wired to the new button.
- [exact] Ensure `snippets.json` remains valid JSON after any add/remove operation.
- [exact] After removal, the Entry widget should show empty text, not crash.

Rollback: `git checkout -- gui/main_window.py multiclip.py`

Verification:
- Manual: Select a Clipman item. Click "Send to Snippet". Choose S3. Verify S3 entry shows the text. Restart app. Verify S3 still shows the text.
- Manual: Click X on S3. Verify entry clears. Check `snippets.json` — key "2" (0-indexed) should be absent or empty.
- Manual: Select 3 Clipman items. Click "Send to Snippet". Choose S1. Verify S1, S2, S3 are filled sequentially.

Exit criteria: "Send to Snippet" works for single and multiple items. X button clears snippet and persists. No JSON corruption. Snippets survive app restart.


---

Branch: multiclip-step-06-visual-transfer-feedback
Size: S
Isolation: main-tree
Agent: default
Context (cold-start brief):
The V3 spec requires visual feedback on every transfer: a ~2-second slow pulse (gold or bright green background) on the destination slot, plus a status bar message. This step instruments all existing transfer call sites added in Steps 01-05.

Transfer sites to instrument:
1. `_transfer_clipman_to_og_slots` (Block Bundle, 1 slot per line)
2. `_send_to_snippets` (Send to Snippet)
3. Orderly auto-capture (Step 03)

The flash animation can be implemented via `tk.after()` scheduling: toggle background color on/off every 200ms for 2 seconds (5 pulses). Use the existing `SlotDisplay.container` widget reference.

Key file: `gui/main_window.py`.

Tasks:
- [guided] In `gui/main_window.py`, add a method `_flash_slot(slot_id: int, color: str = "#ffd700", duration_ms: int = 2000)`:
  - Store original background color.
  - Schedule alternating color/restores via `self.root.after()`.
  - After duration, restore original color.
- [guided] Add `_flash_snippet(idx: int)` with similar logic on the snippet row background.
- [guided] Call `_flash_slot` after each successful Workbench transfer in `_transfer_clipman_to_og_slots` (iterate the filled slots and flash each).
- [guided] Call `_flash_slot` in Orderly auto-capture (flash the slot that was just written).
- [guided] Call `_flash_snippet` after Send-to-Snippet.
- [exact] Ensure flashes do not stack infinitely if the user transfers rapidly. If a slot is already flashing, restart the flash sequence rather than layering multiple timers.

Rollback: `git checkout -- gui/main_window.py`

Verification:
- Manual: Transfer 3 items to Workbench. Verify 3 slots pulse gold sequentially.
- Manual: Send item to Snippet S2. Verify S2 row pulses.
- Manual: Copy text while Orderly active. Verify the filled slot pulses.
- Manual: Rapid-fire transfers. Verify flashes restart cleanly without visual glitches.

Exit criteria: Every transfer type produces a visible flash on its destination. Flash lasts ~2 seconds. Rapid transfers restart flash cleanly. No tkinter "too many callbacks" errors.

---

Branch: multiclip-step-07-preview-popup-enhancement
Size: S
Isolation: main-tree
Agent: default
Context (cold-start brief):
The existing `ClipmanPreviewPopup` class in `gui/main_window.py` already supports double-click preview with Single/Show All modes and Prev/Next navigation. The V3 spec requires adding a Transfer capability inside the same popup:
- A number input field (1-30) + a "Transfer" button.
- Clicking Transfer sends the currently viewed item to that Workbench slot.

This avoids the user needing to close the preview, select the item, and click Block Bundle.

Key file: `gui/main_window.py`.

Tasks:
- [guided] In `ClipmanPreviewPopup._create_widgets`, add a transfer bar below the navigation bar:
  - `ttk.Label`: `"Transfer to slot:"`
  - `ttk.Spinbox` (from 1 to 30, default 1)
  - `ttk.Button`: `"Transfer"` command calls `_transfer_current_to_slot()`
- [guided] Add `_transfer_current_to_slot()`:
  - Reads spinbox value.
  - Gets current entry content (`self.entries[self.current_idx]`).
  - Calls the main app's transfer callback with that single item, targeting the specified slot directly (bypassing the "next empty slot" logic).
  - Shows a brief confirmation in the popup title or a label.
- [exact] Ensure the popup remains open after Transfer so the user can continue browsing.
- [exact] Disable Transfer button if no entries are loaded.

Rollback: `git checkout -- gui/main_window.py`

Verification:
- Manual: Double-click a Clipman item. Preview opens. Enter slot 7. Click Transfer. Verify slot 7 receives the item. Verify popup stays open.
- Manual: Click Prev/Next in the popup. Verify the spinbox value persists (or resets to 1 — either behavior is acceptable if documented).
- Manual: Click Transfer for a slot that already has content. Verify it overwrites silently (no extra dialog inside popup; the user explicitly chose the slot).

Exit criteria: Preview popup has slot spinbox + Transfer button. Transfer sends current item to chosen slot. Popup remains open. Works in both Single and Show All modes.


---

Branch: multiclip-step-08-integration-testing-and-polish
Size: M
Isolation: main-tree
Agent: strongest
Context (cold-start brief):
All V3 features have been implemented across Steps 01-07. This final integration step verifies that everything works together without regressions. The working core (LCtrl+LAlt copy, RCtrl+RAlt paste, root boot stability) is the highest-priority invariant.

Because this app requires X11 and root privileges for full hotkey testing, the AI performs UI-state and logic-path verification. The user performs the actual hotkey testing.

Tasks:
- [exact] Launch the app: `cd /home/flintx/multiclip && python3 multiclip.py &`
- [exact] Verify the UI loads with all V3 elements visible:
  - Workbench 30 slots (left)
  - Snippets 8 rows (bottom-left)
  - Clipman History panel (right) with Block Bundle, 1 slot per line, Lock Selection, Mode toggle
  - FIFO/LIFO buttons appear only when Orderly mode is active
- [guided] Run through the full V3 feature matrix:
  | Feature | Test Action | Expected Result |
  |---|---|---|
  | Block Bundle | Select 3 Clipman items, click Block Bundle | 3 slots filled |
  | 1 slot per line (Auto) | Select 2 items, mode=Auto, click 1 slot per line | 2 slots filled next empty |
  | 1 slot per line (Manual) | Click slot 10, select 2 items, mode=Manual, click 1 slot per line | slots 10, 11 filled |
  | Orderly capture | Activate Orderly, copy text externally | auto-fills next slot |
  | Orderly FIFO paste | Fill slots 1-3, trigger FIFO paste | pastes 1, then 2, then 3 |
  | Orderly LIFO paste | Fill slots 1-3, switch LIFO, trigger paste | pastes 3, then 2, then 1 |
  | Send to Snippet | Select item, click Send to Snippet, choose S5 | S5 filled, persists |
  | Snippet X remove | Click X on S5 | S5 clears, persists |
  | Visual flash | Any transfer above | destination pulses gold |
  | Preview transfer | Double-click item, enter slot 15, Transfer | slot 15 filled |
  | Slots full dialog | Fill all 30, attempt transfer | warning dialog appears |
- [exact] Verify `clipboard_dict.json` and `snippets.json` remain valid JSON after all operations.
- [exact] Verify no exceptions in terminal output during testing.
- [exact] Verify existing hotkeys (LCtrl+LAlt+1, RCtrl+RAlt+1) still work in Multiclip mode.
- [guided] Create a brief `docs/V3_TEST_RESULTS.md` recording what was tested and the outcome of each test. Mark user-tested items as `[USER]`.

Rollback: `git checkout -- multiclip.py gui/main_window.py docs/V3_TEST_RESULTS.md`

Verification:
- Automated: `python3 -m py_compile multiclip.py gui/main_window.py shared/*.py` — zero syntax errors.
- Automated: `python3 -c "import json; json.load(open('clipboard_dict.json')); json.load(open('snippets.json'))"` — valid JSON.
- Manual: All items in the feature matrix above produce expected results.
- Manual: App exits cleanly (no dangling threads, no flock left locked).

Exit criteria: All V3 features work individually and in combination. Core hotkeys unchanged. JSON files valid. No terminal exceptions. `docs/V3_TEST_RESULTS.md` exists with recorded outcomes.

---

Dependency Graph

```
Step 01 (Button renames + toggle)
  └──→ Step 02 (1 slot per line logic)
         └──→ Step 06 (Visual flash) ──→ Step 08 (Integration)
Step 03 (Orderly core logic)
  └──→ Step 04 (Orderly UI) ──→ Step 06 (Visual flash)
Step 05 (Snippets transfer + removal)
  └──→ Step 06 (Visual flash)
Step 07 (Preview popup enhancement)
  └──→ Step 08 (Integration)
```

Parallelizable:
- Group A: Steps 01 and 03 can be developed concurrently — Step 01 touches only UI labels/widgets; Step 03 touches only `multiclip.py` core logic. No shared files during implementation (they wire together in Steps 02 and 04).
- Group B: Step 05 and Step 07 are independent of each other and can run in parallel after Step 01 is complete (they both touch `gui/main_window.py` but in different widget trees; manual coordination needed to avoid merge conflicts on the same line ranges).
- Step 06 must wait for Steps 02, 04, 05 because it instruments their transfer call sites.
- Step 08 must wait for all other steps.


---

Progress Log

This table is the single source of truth for execution state.

| Step | Status | Notes |
|---|---|---|
| 01 | [ ] | — |
| 02 | [ ] | — |
| 03 | [ ] | — |
| 04 | [ ] | — |
| 05 | [ ] | — |
| 06 | [ ] | — |
| 07 | [ ] | — |
| 08 | [ ] | — |

---

Review Log

- 2026-05-26: Plan author — Reviewed `multiclip-v3-spec.md`, `CLIPMAN_INTEGRATION_SPEC.md`, and current code. Identified that Orderly mode is the riskiest change (touches hotkey-adjacent code). Split into core (Step 03) + UI (Step 04). Identified that Snippets transfer and removal touch the same panel — bundled into Step 05. Verified existing `_transfer_clipman_to_og_slots` already has the "slots full" dialog, so Step 02 only needs to add `start_slot` parameter and wrap-around.

---

Plan Mutation Protocol

When execution diverges from the plan structure, mutate the plan and record the change:

- **Split**: rename Step N -> Step Na, create Step Nb. If a letter-suffixed step needs further splitting, append a numeral (05a -> 05a1, 05a2). Update dependency graph. Log reason in Progress Log.
- **Insert**: use letter suffix (e.g., Step 05a) to avoid renumbering. If the target suffix already exists (from a prior split), use the next available letter. New step must pass cold-start test (self-contained Context).
- **Skip**: mark `[SKIP]` with reason. Never delete — skipped steps are historical record that prevents re-attempting failed approaches.
- **Reorder**: only if dependency graph allows. Verify no step reads output from a step that now executes after it.
- **Abandon**: mark `## Status: ABANDONED — {reason}`. Log lessons in Review Log. Do not delete the file.
- **Scope change**: >50% of remaining steps affected -> ask user whether to continue mutating or create a new plan.

To resume a partially-executed plan in a new session:

1. Read the plan file (objective, constraints, invariants, dependency graph).
2. Read Progress Log — find last `[x]` step and any `[>]` step.
3. If a step is `[>]`: check file state against exit criteria to assess completion. If criteria are not met, continue from where the previous session left off.
4. Read Review Log for context on past issues and decisions.
5. Resume from the first `[ ]` or `[>]` step. Do not re-execute `[x]` or `[SKIP]` steps.

