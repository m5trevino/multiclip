# Research: MultiClip V2 Codebase — Clipboard Data Flow, Slots, Hotkeys, Snippets, and ClipmanParser Replacement Analysis

**Date**: 2026-05-26

## 1. Executive Summary

MultiClip V2 is a Python 3.11 tkinter clipboard manager running on MX Linux (XFCE). It uses `pynput` for global hotkey capture, `pyperclip`/`pyautogui` for clipboard manipulation and paste injection, and reads xfce4-clipman history from a raw textsrc file via `ClipmanParser`. The application supports 30 numbered slots persisted to `clipboard_dict.json`, an embedded snippet system persisted to `snippets.json`, and a dual-pane GUI (`gui/main_window.py`) showing the slot workbench and a Clipman history panel. This research maps the exact data flow, slot management, hotkey registration, snippet system, and the delta required to replace `ClipmanParser` with a self-owned JSON history file.

---

## 2. Technical Context

### 2.1 Entry Point & Bootstrap
- **File**: `multiclip.py:1–408`
- `MultiClipV2.__init__` performs the following bootstrap sequence:
  1. Single-instance guard via `fcntl.flock` on `/tmp/multiclip.lock` (`multiclip.py:128–138`)
  2. Loads 30 slots from `clipboard_dict.json` (`multiclip.py:39–40`, `78–103`)
  3. Registers `pynput` hotkey listener (`multiclip.py:62–63`, `341–387`)
  4. Attempts to load `MainWindow` from `gui/main_window.py` (`multiclip.py:21–26`, `65–71`)
  5. Wires Clipman panel with live polling (`multiclip.py:69`, `140–165`)
  6. Falls back to a simple tkinter UI if the old GUI fails to import (`multiclip.py:72–75`, `233–243`)

### 2.2 Project File Map
| Component | File |
|-----------|------|
| Main application / hotkeys / slot logic | `multiclip.py` |
| GUI (tkinter, dense workbench + Clipman panel) | `gui/main_window.py` |
| Clipman textsrc parser | `shared/clipman_parser.py` |
| Clipboard slot model (unused at runtime by multiclip.py) | `shared/clipboard_manager.py` |
| Snippet persistence | `shared/snippets_manager.py` |
| Config / state manager (largely dormant) | `shared/config_manager.py` |
| History panel (tkinter widgets for clipman entries) | `gui/history_panel.py` |
| Curses CLI browser for clipman | `clipman_cli.py` |
| Slot persistence file | `clipboard_dict.json` |
| Snippet persistence file | `snippets.json` |

---

## 3. Findings & Analysis

### 3.1 Clipboard Data Flow: xfce4-clipman textsrc → ClipmanParser → main_window.py Clipman Panel

**Source file location**
- xfce4-clipman writes its history to `~/.cache/xfce4/clipman/textsrc`.
- `ClipmanParser` hardcodes this path with root-user fallback logic (`shared/clipman_parser.py:58–86`).

**Parsing logic**
- `ClipmanParser.parse(max_entries=200)` reads the entire file, strips the `[texts]\ntexts=` header, splits on unescaped semicolons, reverses the list so newest is first, and returns `List[ClipEntry]` (`shared/clipman_parser.py:89–120`).
- `ClipEntry._decode()` handles escape sequences `\;`, `\n`, `\s`, `\t`, `\r` (`shared/clipman_parser.py:26–33`).
- `ClipEntry._make_preview()` generates an 80-char single-line preview from the first non-empty line (`shared/clipman_parser.py:35–46`).

**Flow into the GUI**
1. `MultiClipV2._wire_clipman_panel()` instantiates `ClipmanParser()`, calls `parser.parse(max_entries=9999)`, and passes the entries to `MainWindow.set_clipman_entries()` (`multiclip.py:140–149`).
2. `MainWindow.set_clipman_entries(entries)` stores the full list and renders paginated pages of 50 items into a `tk.Listbox` (`gui/main_window.py:528–533`, `535–549`).
3. Live refresh is started via `start_live_clipman_refresh(parser, interval_ms=3000)` (`multiclip.py:155–156`).
4. `MainWindow._poll_clipman()` polls the textsrc file mtime every 3 seconds; on change it calls `parser.get_recent(80)` and updates the listbox (`gui/main_window.py:579–599`).

**Transfer back to OG slots**
- GUI buttons trigger `_on_clipman_transfer_batch()` or `_on_clipman_transfer_one_slot()`, which call `self.clipman_transfer_callback` — wired in `multiclip.py:152` to `MultiClipV2._transfer_clipman_to_og_slots()` (`gui/main_window.py:624–646`, `multiclip.py:167–231`).
- That callback fills empty slots 1–30 first, then prompts the user via `simpledialog.askinteger` if all slots are full (`multiclip.py:186–210`).

**Key observation**: There is no bidirectional sync. MultiClip *reads* from clipman but never writes to the textsrc file. The textsrc file is owned entirely by xfce4-clipman.

---

### 3.2 Slot Management in multiclip.py

**Data structure**
- `MultiClipV2.slots` is a flat `dict` keyed by strings `"1"` through `"30"`, initialized empty (`multiclip.py:39`).

**Persistence format (`clipboard_dict.json`)**
- Saved as `{"slots": {"1": "...", "2": "...", ...}}` (`multiclip.py:101–103`).
- Loader is defensive: handles legacy flat dicts, nested dicts with `"content"` keys, and keys prefixed with `"slot_"` (`multiclip.py:78–99`).

**`add_to_slot(slot_num: int)`** (`multiclip.py:270–286`)
1. Releases all modifiers via `pyautogui.keyUp` + 80 ms sleep.
2. Sends `ctrl+c` via `pyautogui.hotkey`.
3. Sleeps 160 ms.
4. Reads clipboard via `pyperclip.paste()`.
5. If non-empty, stores in `self.slots[str(slot_num)]`, calls `save_slots()`, and shows a toast.

**`paste_from_slot(slot_num: int)`** (`multiclip.py:288–330`)
1. Retrieves content from `self.slots`.
2. Copies it to system clipboard via `pyperclip.copy`.
3. Sleeps 120 ms for clipboard settle.
4. Detects active window terminal class via `xdotool getactivewindow` + `xprop WM_CLASS` (`multiclip.py:332–338`).
5. Injects paste keystrokes:
   - Terminal: `xdotool key --clearmodifiers ctrl+shift+v`
   - Non-terminal: `xdotool key --clearmodifiers ctrl+v`
6. Falls back to `pyautogui.hotkey` if `xdotool` fails.

**Slot display in GUI**
- `MainWindow` renders 30 `SlotDisplay` widgets in a 2-column grid (left 1–15, right 16–30) inside a scrollable canvas (`gui/main_window.py:330–371`).
- Each `SlotDisplay` shows an order field, slot ID label, preview label (click to select, right-click to edit), and character count (`gui/main_window.py:187–256`).

---

### 3.3 Hotkey Registration Flow (pynput Listener)

**Registration** (`multiclip.py:341–387`)
- `pynput.keyboard.Listener` is created with `on_press` and `on_release` callbacks.
- The listener runs in a background thread (`self.listener.start()` at `multiclip.py:386`).

**Modifier tracking**
- `self.held_mods` is a `set()` tracking `'ctrl_l'`, `'ctrl_r'`, `'alt_l'`, `'alt_r'`, `'ctrl'`, `'alt'` (`multiclip.py:43`).
- `on_press` inspects `str(key).lower()` for substring matches (`'ctrl'` / `'alt'` / `'left'` / `'right'`) and adds to `held_mods` (`multiclip.py:342–358`).
- `on_release` performs symmetric removal (`multiclip.py:367–383`).

**Digit dispatch**
- When a digit key is pressed (`key.char.isdigit()`), the slot is computed as `10 if digit == '0' else int(digit)` (`multiclip.py:360–362`).
- `_handle_combo(slot)` is called immediately on digit press — there is no separate "release" trigger for the combo (`multiclip.py:389–398`).

**Combo decision logic** (`multiclip.py:389–398`)
- **Paste (right-side combo)**: If `has_right` is true (`ctrl_r` or `alt_r` in `held_mods`) AND either `ctrl_r`/`ctrl` AND either `alt_r`/`alt` are present → calls `paste_from_slot(slot)`.
- **Copy (left-side combo)**: Else if `ctrl` and `alt` are present (or `ctrl_l` and `alt_l`) → calls `add_to_slot(slot)`.
- This means pressing `LCtrl+LAlt+1` copies to slot 1; pressing `RCtrl+RAlt+1` pastes from slot 1.

**Important caveat**: Because the digit triggers on `press`, the modifier keys must already be held. The code does not use `pynput` hotkey combinations; it manually tracks modifiers. This can lead to misfires if key event ordering is inconsistent.

---

### 3.4 Snippet System

**Two snippet subsystems exist** — one in `shared/snippets_manager.py` and one embedded directly in `gui/main_window.py`.

**`SnippetVault` (`shared/snippets_manager.py:1–46`)**
- File path hardcoded to `/home/flintx/multiclip/snippets.json`.
- Stores 20 string entries keyed by integer index (`0–19`).
- `set_snippet(index, content)` writes immediately to disk (`shared/snippets_manager.py:15–18`).
- `load()` seeds defaults if the file is missing: email, tunnel alias, proxy exports, pip note (`shared/snippets_manager.py:32–37`).
- **Status**: Imported nowhere in `multiclip.py` or `gui/main_window.py`. This module is effectively dead code in the current runtime.

**GUI Embedded Snippets (`gui/main_window.py:373–393`)**
- `MainWindow._create_ui()` builds a "SNIPPETS (persistent)" panel with 8 `tk.Entry` widgets (`S1`–`S8`).
- Each row has a Save button calling `_save_snippet(idx)`.
- Snippets file path is computed relative to `gui/main_window.py`: `../snippets.json` (`gui/main_window.py:392`).
- `_load_snippets()` reads the JSON dict and populates entries on startup (`gui/main_window.py:649–662`).
- `_save_snippet(idx)` reads the existing file, updates the key, and writes back (`gui/main_window.py:664–678`).
- **Status**: This is the live snippet UI. The user interacts with these 8 entries directly.

**Vault Panel (`gui/main_window.py:399–425`)**
- A separate "SNIPPET VAULT" with 10 entries (`V1`–`V10`) exists in the right panel, but `vault_panel.pack()` is never called in `_show_mode_panel` — it is effectively hidden because `_show_mode_panel` only calls `pack_forget()` on it and never shows it (`gui/main_window.py:688–693`).

---

### 3.5 Replacing ClipmanParser with a Self-Owned JSON History File

To replace `ClipmanParser` (which reads `~/.cache/xfce4/clipman/textsrc`) with a self-owned JSON history file, the following changes would be required:

**A. Data format change**
- Current: `ClipmanParser` parses a custom semicolon-delimited, escape-encoded plain-text file.
- New: A JSON file (e.g., `~/.multiclip/history.json`) structured as a list of objects: `[{"content": "...", "timestamp": "...", "preview": "..."}, ...]`.
- `ClipEntry` dataclass already has `id`, `content`, `preview`, `word_count`, and `decoded_content` — these map cleanly to JSON fields.

**B. Files requiring modification**

| File | Lines | Change |
|------|-------|--------|
| `shared/clipman_parser.py` | 53–157 | Replace `parse()` with a JSON reader. Keep `ClipEntry` as the return type so callers are unaffected. Alternatively, create a new `JsonHistoryParser` class with the same interface (`parse(max_entries)`, `get_recent(count)`). |
| `multiclip.py` | 18 | Change import from `ClipmanParser` to new parser, or make parser selection configurable. |
| `multiclip.py` | 140–165 | `_wire_clipman_panel()` currently passes `parser` to `start_live_clipman_refresh()`. The mtime polling logic (`_poll_clipman`) would work on the JSON file as well. |
| `gui/main_window.py` | 579–599 | `_poll_clipman()` reads `parser.filepath` and `parser.get_recent(80)`. If the new parser exposes the same attributes, no GUI changes are needed. |
| `clipman_cli.py` | 40–54 | `ClipmanBrowser` instantiates `ClipmanParser()` directly. Would need to instantiate the new parser or accept it as a parameter. |
| `gui/history_panel.py` | 98, 217 | `HistoryPanel` takes `parser` in `__init__` and calls `parser.parse()` and `parser.search()`. A new parser must implement `search(query, max_results)` or that call must be handled elsewhere. |

**C. Write-path requirement**
- Currently MultiClip never writes clipboard history; it only reads from xfce4-clipman.
- A self-owned JSON file implies MultiClip must also **capture** clipboard changes itself and append them to the JSON history.
- This would require:
  1. A background clipboard polling thread (or `pynput` integration) to detect new clipboard content.
  2. Deduplication logic (skip if identical to the most recent entry).
  3. A max-history cap and rotation policy (e.g., keep last 500 entries).
  4. Atomic file writes to avoid JSON corruption.

**D. Existing `ConfigManager` hook**
- `ConfigManager` already defines `behavior.max_clipboard_history = 100` (`shared/config_manager.py:40`), but this setting is unused anywhere in the codebase. It could be wired to the new history writer.

**E. Migration path**
- On first run, the new parser could attempt to import legacy xfce4-clipman textsrc data into the JSON file, then switch to JSON as the source of truth.
- `ClipmanParser` could be kept as a one-shot migration utility.

---

## 4. Technical Constraints

1. **Root-user clipboard access**: The app is designed to run as root sometimes. `pyperclip` and `xdotool` behavior under root+X11 is flaky; the code includes 120–160 ms sleeps and `xdotool` fallbacks specifically for this (`multiclip.py:273–330`). Any new clipboard capture thread must also handle root contexts.

2. **xfce4-clipman dependency is one-way read-only**: The current architecture treats clipman as an external oracle. Removing it means MultiClip must become its own clipboard monitor.

3. **`history_panel.py` references `parser.search()`**: `gui/history_panel.py:227` calls `self.parser.search(query, max_results=200)`. `ClipmanParser` does **not** implement a `search()` method — this call will raise `AttributeError` if executed. It appears `history_panel.py` is either unused or untested in the current runtime, since `multiclip.py` wires the Clipman panel through `main_window.py` directly, not through `HistoryPanel`.

4. **Dead code**: `shared/clipboard_manager.py` (`ClipboardManager` / `ClipboardSlot`) and `shared/snippets_manager.py` (`SnippetVault`) are not imported or used by `multiclip.py`. The live slot store is a plain `dict` in `MultiClipV2`, and the live snippets are managed inside `MainWindow`.

5. **Hotkey collision risk**: The modifier-tracking hotkey system does not distinguish between `Ctrl+Alt+1` and `Ctrl+Alt+Shift+1`; any digit press while `ctrl` and `alt` are held will trigger a slot action. Adding more hotkeys (e.g., for snippets or history navigation) would require refactoring `_handle_combo()` or switching to `pynput`'s `GlobalHotKeys`.

---

## 5. Architecture Documentation

### 5.1 Current Data Flow Diagram

```
xfce4-clipman (external)
    │ writes
    ▼
~/.cache/xfce4/clipman/textsrc
    │ read by
    ▼
ClipmanParser.parse() ──► List[ClipEntry]
    │                              │
    │ (CLI)                        │ (GUI)
    ▼                              ▼
clipman_cli.py              MainWindow.set_clipman_entries()
(Curses browser)            ├─ tk.Listbox (paginated 50/page)
                            ├─ Live poll every 3s via mtime
                            └─ Transfer callback
                                       │
                                       ▼
                         MultiClipV2._transfer_clipman_to_og_slots()
                                       │
                                       ▼
                         self.slots["1".."30"]  ◄────  add_to_slot() / paste_from_slot()
                                       │
                                       ▼
                         clipboard_dict.json (persisted)
```

### 5.2 Slot Write Path (Copy)

```
User presses LCtrl + LAlt + [0-9]
    │
    ▼
pynput Listener.on_press ──► _handle_combo(slot)
    │
    ▼
add_to_slot(slot_num)
    ├─ pyautogui.hotkey("ctrl", "c")
    ├─ pyperclip.paste()
    ├─ self.slots[str(slot_num)] = content
    ├─ save_slots() ──► clipboard_dict.json
    └─ show_toast() ──► notify-send
```

### 5.3 Slot Read Path (Paste)

```
User presses RCtrl + RAlt + [0-9]
    │
    ▼
pynput Listener.on_press ──► _handle_combo(slot)
    │
    ▼
paste_from_slot(slot_num)
    ├─ pyperclip.copy(content)
    ├─ _is_terminal()? (xdotool + xprop)
    ├─ xdotool key --clearmodifiers ctrl(+shift)+v
    └─ show_toast() ──► notify-send
```

### 5.4 Conventions Found
- **Defensive JSON loading**: Both `multiclip.py` and `gui/main_window.py` wrap file I/O in broad `try/except` blocks and silently ignore failures.
- **Hardcoded paths**: `chargers.png`, `snippets.json`, and `clipboard_dict.json` use paths relative to `__file__` or absolute `/home/flintx/multiclip/` paths.
- **Signal/atexit safety**: `multiclip.py` registers `SIGINT`/`SIGTERM` handlers and `atexit` to force-save slots.
- **No tests are wired to CI**: Test files (`test_hotkeys.py`, `test_clipman_parser.py`, etc.) exist but are not executed automatically.
