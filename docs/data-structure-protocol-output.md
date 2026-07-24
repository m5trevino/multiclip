# MultiClip — Data Structure Protocol (DSP) Output

> **Generated:** 2026-05-26T00:21:10-07:00  
> **Project Root:** `/home/flintx/multiclip`  
> **DSP Version:** v1.0 (initialized via `dsp-cli.py`)  
> **Skill:** `data-structure-protocol`  

---

## 1. Executive Summary

**MultiClip** is a Linux clipboard manager built for MX Linux / XFCE. It provides 30 persistent clipboard slots, global hotkey capture (Ctrl+Alt+Digit), integration with the XFCE Clipman history, a dense Tkinter GUI, a curses-based CLI browser, and a text-diff comparison module. The application enforces single-instance via `fcntl` flock and runs as a systemd user service.

**Architecture Pattern:** Modular monolith — core logic lives in `shared/`, GUI in `gui/`, diff tooling in `diff_marker/`, with `multiclip.py` as the orchestrating entrypoint.

---

## 2. DSP Graph Statistics

| Metric | Count |
|--------|-------|
| **Total Entities** | 48 |
| **Objects** (modules / files / configs) | 15 |
| **Functions** (public methods / entrypoints) | 16 |
| **External Dependencies** | 17 |
| **Import Relationships** | 61 |
| **Shared / Exported APIs** | 16 |
| **Circular Dependencies** | 0 |
| **Orphan Entities** | 3 |

### Orphans (safe — non-code artifacts)
- `obj-85aa417a` — `snippets.json` (data file, read by `shared/snippets_manager.py`)
- `obj-99da1ecd` — `multiclip.service` (systemd unit, not imported)
- `obj-dbf97a02` — `requirements.txt` (manifest, not imported)

---

## 3. Entity Catalog

### 3.1 Source Objects (Modules / Files)

| UID | Source Path | Kind | Purpose |
|-----|-------------|------|---------|
| `obj-3d8fdd51` | `multiclip.py` | object | Main application entrypoint for MultiClip V2. Initializes hotkey listener, clipboard slots persistence, and launches the Tkinter GUI. |
| `obj-e059eede` | `clipman_cli.py` | object | Curses-based terminal UI for browsing XFCE clipman history. Supports multi-select, ordered selection, and deployment to slots. |
| `obj-8fe32c41` | `shared/clipboard_manager.py` | object | Core clipboard slot management. Defines `ClipboardSlot` and `ClipboardManager` for storing and retrieving up to 30 clipboard items. |
| `obj-fd4043ab` | `shared/clipman_parser.py` | object | Parser for XFCE4 clipman `textsrc` history files. Extracts clipboard entries with escape-sequence decoding and preview generation. |
| `obj-b591ef86` | `shared/config_manager.py` | object | JSON-based configuration and state persistence manager. Handles hotkey configs, GUI settings, behavior options, and snippet storage. |
| `obj-21eca0e7` | `shared/snippets_manager.py` | object | Fixed snippet vault manager. Stores 20 persistent text snippets (emails, commands, proxy settings) in a JSON file. |
| `obj-f72cbc38` | `gui/main_window.py` | object | Tkinter main GUI window. Features dense 30-slot workbench, clipman history panel, snippet vault, pagination, and toast notifications. |
| `obj-75850ccd` | `gui/history_panel.py` | object | Integrated clipman history panel widget for the main GUI. Provides scrollable entry list with search, selection modes, and slot deployment. |
| `obj-5f5075cf` | `diff_marker/diff_types.py` | object | Type definitions for the diff-marker module. Defines `DiffType` enum, `DiffLine`, and `DiffResult` dataclasses with statistics calculation. |
| `obj-f2314cd7` | `diff_marker/diff_manager.py` | object | Text diff calculation engine built on Python `difflib`. Generates unified and side-by-side diffs with line-by-line change tracking. |
| `obj-c96fd17d` | `diff_marker/diff_interface.py` | object | Tkinter diff comparison UI widget. Provides two-panel input, side-by-side/unified view modes, slot integration, and result saving. |
| `obj-983ee118` | `clipboard_dict.json` | object | Persistent JSON storage file for 30 clipboard slots. Auto-saved on slot changes and at process exit. |
| `obj-85aa417a` | `snippets.json` | object | Persistent JSON storage file for fixed text snippets. Pre-loaded with tunnel config, proxy exports, and pip notes. |
| `obj-dbf97a02` | `requirements.txt` | object | Python package dependencies manifest listing `pyperclip`, `pyautogui`, and `pynput`. |
| `obj-99da1ecd` | `multiclip.service` | object | systemd service unit definition for auto-starting multiclip on boot. |

### 3.2 Public Functions (API Surface)

| UID | Source | Owner | Purpose |
|-----|--------|-------|---------|
| `func-a0371af3` | `multiclip.py#MultiClipV2.__init__` | `obj-3d8fdd51` | Main application constructor. Sets up single-instance lock, loads slots, registers hotkeys, wires old UI, and starts mainloop. |
| `func-84824d9a` | `multiclip.py#MultiClipV2.add_to_slot` | `obj-3d8fdd51` | Copy currently selected text into a numbered slot using pyautogui + pyperclip. Shows toast notification. |
| `func-87f59397` | `multiclip.py#MultiClipV2.paste_from_slot` | `obj-3d8fdd51` | Paste content from a numbered slot into the active window. Uses xdotool for reliability under root. |
| `func-f3f4c568` | `multiclip.py#MultiClipV2._transfer_clipman_to_og_slots` | `obj-3d8fdd51` | Transfer selected clipman history entries into OG slots. Fills empty slots first, prompts on full. |
| `func-69e014af` | `multiclip.py#MultiClipV2.run` | `obj-3d8fdd51` | Application run loop. Delegates to Tkinter mainloop if using simple fallback UI. |
| `func-d208c29b` | `clipman_cli.py#main` | `obj-e059eede` | CLI entry point for the curses-based clipman history browser. Parses arguments and launches curses wrapper. |
| `func-f4a7f31c` | `shared/clipboard_manager.py#ClipboardManager.store_in_slot` | `obj-8fe32c41` | Store text content into a numbered clipboard slot. |
| `func-d0dc168d` | `shared/clipboard_manager.py#ClipboardManager.get_slot_content` | `obj-8fe32c41` | Retrieve text content from a numbered clipboard slot. |
| `func-3d9df7c7` | `shared/clipman_parser.py#ClipmanParser.parse` | `obj-fd4043ab` | Parse the XFCE clipman `textsrc` file and return a list of `ClipEntry` objects (newest first). |
| `func-03ea68ec` | `shared/config_manager.py#ConfigManager.get` | `obj-b591ef86` | Retrieve a configuration value by dot-separated key path with optional default fallback. |
| `func-6b5c1981` | `shared/snippets_manager.py#SnippetVault.get_snippet` | `obj-21eca0e7` | Retrieve a fixed snippet by index from the JSON-backed vault. |
| `func-a401c649` | `gui/main_window.py#MainWindow.__init__` | `obj-f72cbc38` | Build the main Tkinter GUI with 30-slot workbench, clipman history, snippets, vault, and toolbar. |
| `func-a8d14d0b` | `gui/main_window.py#MainWindow.run` | `obj-f72cbc38` | Start the Tkinter main event loop for the main window. |
| `func-966eb3cf` | `gui/history_panel.py#HistoryPanel.__init__` | `obj-75850ccd` | Build the integrated history panel widget with canvas scrolling, search, pagination, and deploy controls. |
| `func-36330eb7` | `diff_marker/diff_manager.py#DiffManager.calculate_diff` | `obj-f2314cd7` | Calculate differences between two texts using difflib. Returns `DiffResult` with unified and side-by-side formats. |
| `func-e8349fcf` | `diff_marker/diff_interface.py#DiffInterface.__init__` | `obj-c96fd17d` | Build the Tkinter diff comparison widget with two-panel input, notebook tabs, and color-coded results. |

### 3.3 External Dependencies

| UID | Name | Kind | Purpose |
|-----|------|------|---------|
| `obj-ae9ce61e` | `pyperclip` | external | Cross-platform Python library for clipboard copy/paste operations. |
| `obj-c35d0af5` | `pyautogui` | external | Python GUI automation library for simulating keyboard and mouse events. |
| `obj-eacd95fa` | `pynput` | external | Python library for monitoring and controlling input devices (keyboard listener). |
| `obj-65c1e1dd` | `tkinter` | external | Python standard library GUI toolkit (Tk). Used for all windowing and widgets. |
| `obj-e8da28fd` | `curses` | external | Python standard library terminal UI library for the clipman CLI browser. |
| `obj-8b873984` | `difflib` | external | Python standard library for computing deltas between sequences. Powers diff calculation. |
| `obj-b44bd256` | `json` | external | Python standard library for JSON serialization/deserialization. |
| `obj-ef6002d0` | `subprocess` | external | Python standard library for spawning new processes. Used for notify-send and xdotool. |
| `obj-ce11ddc5` | `os` | external | Python standard library for OS interface. File path operations and environment variables. |
| `obj-ad37706a` | `sys` | external | Python standard library for system-specific parameters and functions. |
| `obj-67ac8964` | `pathlib` | external | Python standard library for object-oriented filesystem paths. |
| `obj-2af6b3e7` | `datetime` | external | Python standard library for date and time manipulation. |
| `obj-40f28de2` | `fcntl` | external | Python standard library for file control operations. Used for single-instance flock. |
| `obj-14efd00e` | `signal` | external | Python standard library for signal handling. Registers SIGINT/SIGTERM handlers for graceful shutdown. |
| `obj-aac1d86b` | `atexit` | external | Python standard library for registering cleanup functions on normal interpreter exit. |
| `obj-997475e4` | `time` | external | Python standard library for time-related functions. Sleep delays for clipboard settling and hotkey timing. |
| `obj-8abf244c` | `argparse` | external | Python standard library for command-line argument parsing. |

---

## 4. Import Graph with Reasons

### 4.1 `multiclip.py` (`obj-3d8fdd51`) — Root Entrypoint

**Imports:**
| Target | Reason |
|--------|--------|
| `obj-ae9ce61e` (pyperclip) | Copy/paste clipboard operations via `pyperclip.paste()` and `pyperclip.copy()` |
| `obj-c35d0af5` (pyautogui) | Simulate Ctrl+C hotkey and keyboard release for slot capture and paste injection |
| `obj-ef6002d0` (subprocess) | Spawn `notify-send` for toast notifications, `xdotool` for paste injection, and `xprop` for terminal detection |
| `obj-997475e4` (time) | Sleep delays for clipboard settling and modifier release timing |
| `obj-b44bd256` (json) | Serialize and deserialize clipboard slots to `clipboard_dict.json` |
| `obj-ce11ddc5` (os) | File path construction for `dict_file`, `icon_path`, and environment variable checks |
| `obj-ad37706a` (sys) | Process exit on single-instance lock failure and signal handling |
| `obj-40f28de2` (fcntl) | Exclusive flock on `/tmp/multiclip.lock` to enforce single application instance |
| `obj-65c1e1dd` (tkinter) | Simple fallback UI built with `tkinter.Tk` when old GUI fails to load |
| `obj-eacd95fa` (pynput) | Global keyboard listener for Ctrl+Alt+Digit hotkey combos across all applications |
| `obj-fd4043ab` (shared/clipman_parser.py) | Parse XFCE clipman history to populate the right-side history panel |
| `obj-f72cbc38` (gui/main_window.py) | Load the old dense Tkinter GUI with 30-slot workbench and clipman integration |
| `obj-983ee118` (clipboard_dict.json) | Read and write persistent slot storage on startup and slot changes |
| `obj-14efd00e` (signal) | Register SIGINT/SIGTERM handlers for graceful emergency slot save on kill |
| `obj-aac1d86b` (atexit) | Register emergency save callback on normal interpreter exit |

**Exports:** `func-a0371af3`, `func-84824d9a`, `func-87f59397`, `func-f3f4c568`, `func-69e014af`

---

### 4.2 `clipman_cli.py` (`obj-e059eede`) — Curses Browser

**Imports:**
| Target | Reason |
|--------|--------|
| `obj-e8da28fd` (curses) | Terminal-based curses UI for browsing clipman history with colors and keyboard input |
| `obj-ce11ddc5` (os) | File path operations for deploy queue directory and `expanduser` |
| `obj-ad37706a` (sys) | Manipulate `sys.path` to include shared module and exit on interrupts |
| `obj-b44bd256` (json) | Serialize deploy queue selections to JSON file for multiclip to consume |
| `obj-fd4043ab` (shared/clipman_parser.py) | Parse XFCE clipman textsrc to load history entries into the browser |
| `obj-2af6b3e7` (datetime) | Timestamp for deploy queue file to track when selections were made |
| `obj-8abf244c` (argparse) | Parse command-line arguments (`--max` entries limit) |

**Exports:** `func-d208c29b`

---

### 4.3 `shared/clipboard_manager.py` (`obj-8fe32c41`)

**Imports:**
| Target | Reason |
|--------|--------|
| `obj-ae9ce61e` (pyperclip) | Clipboard access (imported but current implementation uses in-memory storage only) |
| `obj-b44bd256` (json) | JSON serialization for potential slot export (not actively used in shown code) |
| `obj-2af6b3e7` (datetime) | Timestamp slot updates for ordering and freshness tracking |

**Exports:** `func-f4a7f31c`, `func-d0dc168d`

**Who imports this:**
- `obj-c96fd17d` (diff_marker/diff_interface.py) — *"Load slot content and save diff results back to clipboard slots"*

---

### 4.4 `shared/clipman_parser.py` (`obj-fd4043ab`)

**Imports:**
| Target | Reason |
|--------|--------|
| `obj-ce11ddc5` (os) | File existence checks, `expanduser` for home directory, and filepath resolution |
| `obj-b44bd256` (json) | Not directly used in parser (`dataclasses` and `typing` are primary imports) |

**Exports:** `func-3d9df7c7`

**Who imports this:**
- `obj-3d8fdd51` (multiclip.py) — *"Parse XFCE clipman history to populate the right-side history panel"*
- `obj-75850ccd` (gui/history_panel.py) — *"Parse clipman history and perform search queries against the textsrc database"*
- `obj-e059eede` (clipman_cli.py) — *"Parse XFCE clipman textsrc to load history entries into the browser"*

---

### 4.5 `shared/config_manager.py` (`obj-b591ef86`)

**Imports:**
| Target | Reason |
|--------|--------|
| `obj-b44bd256` (json) | Read and write JSON config, state, and snippets files |
| `obj-ce11ddc5` (os) | OS path operations (not heavily used, `pathlib` preferred) |
| `obj-67ac8964` (pathlib) | Object-oriented filesystem paths for config directory and file resolution |

**Exports:** `func-03ea68ec`

---

### 4.6 `shared/snippets_manager.py` (`obj-21eca0e7`)

**Imports:**
| Target | Reason |
|--------|--------|
| `obj-b44bd256` (json) | Read and write `snippets.json` persistence file |
| `obj-ce11ddc5` (os) | File existence check before loading `snippets.json` |

**Exports:** `func-6b5c1981`

---

### 4.7 `gui/main_window.py` (`obj-f72cbc38`)

**Imports:**
| Target | Reason |
|--------|--------|
| `obj-65c1e1dd` (tkinter) | Tkinter widgets for the entire GUI: `Tk`, `Frame`, `Label`, `Button`, `Canvas`, `Scrollbar`, `Listbox`, `Entry`, `Toplevel`, `PhotoImage`, `StringVar`, `Radiobutton` |
| `obj-b44bd256` (json) | Load and save `snippets.json` for the bottom-left snippets panel |
| `obj-ce11ddc5` (os) | File path construction for `snippets.json` and `chargers.png` logo |

**Exports:** `func-a401c649`, `func-a8d14d0b`

**Who imports this:**
- `obj-3d8fdd51` (multiclip.py) — *"Load the old dense Tkinter GUI with 30-slot workbench and clipman integration"*

---

### 4.8 `gui/history_panel.py` (`obj-75850ccd`)

**Imports:**
| Target | Reason |
|--------|--------|
| `obj-65c1e1dd` (tkinter) | Tkinter widgets for scrollable history list: `Canvas`, `Frame`, `Scrollbar`, `Listbox`, `Entry` |
| `obj-ae9ce61e` (pyperclip) | Copy full entry text to system clipboard on double-click |
| `obj-fd4043ab` (shared/clipman_parser.py) | Parse clipman history and perform search queries against the textsrc database |

**Exports:** `func-966eb3cf`

---

### 4.9 `diff_marker/diff_types.py` (`obj-5f5075cf`)

**Imports:**
| Target | Reason |
|--------|--------|
| `obj-8b873984` (difflib) | Not directly used; `enum` and `dataclasses` are primary imports |

**Who imports this:**
- `obj-f2314cd7` (diff_marker/diff_manager.py) — *"DiffResult and DiffType for displaying color-coded comparison results"*

---

### 4.10 `diff_marker/diff_manager.py` (`obj-f2314cd7`)

**Imports:**
| Target | Reason |
|--------|--------|
| `obj-8b873984` (difflib) | `SequenceMatcher` and `unified_diff` for calculating text differences |
| `obj-5f5075cf` (diff_marker/diff_types.py) | `DiffResult`, `DiffLine`, `DiffType` dataclasses for structured diff output |

**Exports:** `func-36330eb7`

**Who imports this:**
- `obj-c96fd17d` (diff_marker/diff_interface.py) — *"Calculate diffs and format statistics for display in the result tab"*

---

### 4.11 `diff_marker/diff_interface.py` (`obj-c96fd17d`)

**Imports:**
| Target | Reason |
|--------|--------|
| `obj-65c1e1dd` (tkinter) | Tkinter widgets for two-panel diff UI: `Text`, `Notebook`, `PanedWindow`, `Toplevel` |
| `obj-ae9ce61e` (pyperclip) | Paste system clipboard content into diff input panels |
| `obj-f2314cd7` (diff_marker/diff_manager.py) | Calculate diffs and format statistics for display in the result tab |
| `obj-8fe32c41` (shared/clipboard_manager.py) | Load slot content and save diff results back to clipboard slots |

**Exports:** `func-e8349fcf`

---

### 4.12 Data / Config Files

| Entity | Consumers | Reason |
|--------|-----------|--------|
| `obj-983ee118` (clipboard_dict.json) | `obj-3d8fdd51` | Read and write persistent slot storage on startup and slot changes |
| `obj-85aa417a` (snippets.json) | *(orphan — read by `SnippetVault` at runtime)* | Persistent JSON storage for fixed text snippets |
| `obj-99da1ecd` (multiclip.service) | *(orphan — consumed by systemd externally)* | systemd service unit definition for auto-starting multiclip on boot |
| `obj-dbf97a02` (requirements.txt) | *(orphan — consumed by pip externally)* | Python package dependencies manifest |

---

## 5. Module Dependency Map

```
                    ┌─────────────────────────────────────────┐
                    │         multiclip.py (ROOT)             │
                    │  obj-3d8fdd51  [func-a0371af3 ...]      │
                    └────────────┬────────────────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│  gui/main_window │  │ shared/clipman_parser│  │  clipman_cli.py     │
│  obj-f72cbc38    │  │  obj-fd4043ab        │  │  obj-e059eede       │
└─────────────────┘  └─────────────────────┘  └─────────────────────┘
          │                      │                      │
          │                      ▼                      │
          │           ┌─────────────────────┐           │
          │           │ gui/history_panel   │           │
          │           │  obj-75850ccd       │           │
          │           └─────────────────────┘           │
          │                                             │
          ▼                                             ▼
┌─────────────────────┐                       ┌─────────────────────┐
│ shared/snippets_mgr │                       │ shared/clipboard_mgr│
│  obj-21eca0e7       │                       │  obj-8fe32c41       │
└─────────────────────┘                       └─────────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────────┐
                                              │ diff_marker/        │
                                              │   diff_interface    │
                                              │   obj-c96fd17d      │
                                              └─────────────────────┘
                                                       │
                                    ┌──────────────────┴──────────────────┐
                                    ▼                                      ▼
                          ┌─────────────────┐                   ┌─────────────────┐
                          │ diff_marker/    │                   │ shared/clipboard│
                          │   diff_manager  │                   │   _manager      │
                          │   obj-f2314cd7  │                   │   obj-8fe32c41  │
                          └─────────────────┘                   └─────────────────┘
                                    │
                                    ▼
                          ┌─────────────────┐
                          │ diff_marker/    │
                          │   diff_types    │
                          │   obj-5f5075cf  │
                          └─────────────────┘
```

---

## 6. Public API Surface

### 6.1 Entrypoints

| Entrypoint | Command / Trigger | Description |
|------------|-------------------|-------------|
| `multiclip.py` | `python multiclip.py` | Main GUI + hotkey daemon. Blocks on Tkinter mainloop. |
| `clipman_cli.py#main` | `python clipman_cli.py [--max N]` | Curses terminal browser. Standalone. |

### 6.2 Key Classes and Their Responsibilities

| Class | Module | Responsibility |
|-------|--------|----------------|
| `MultiClipV2` | `multiclip.py` | Orchestrates slots, hotkeys, UI, and persistence lifecycle. |
| `ClipmanBrowser` | `clipman_cli.py` | Curses UI for history browsing with multi-select and ordered deployment. |
| `ClipboardManager` | `shared/clipboard_manager.py` | In-memory slot storage with ordering support. |
| `ClipmanParser` | `shared/clipman_parser.py` | Reads `~/.cache/xfce4/clipman/textsrc` and decodes escape sequences. |
| `ConfigManager` | `shared/config_manager.py` | Merged default + user JSON config with dot-path getter/setter. |
| `SnippetVault` | `shared/snippets_manager.py` | Fixed snippet persistence with hard-coded defaults. |
| `MainWindow` | `gui/main_window.py` | Dense Tkinter GUI: 2-column slot grid, clipman panel, vault, snippets, toast. |
| `HistoryPanel` | `gui/history_panel.py` | Scrollable clipman history with canvas-based virtualization. |
| `DiffManager` | `diff_marker/diff_manager.py` | Text diff engine using `difflib.SequenceMatcher`. |
| `DiffInterface` | `diff_marker/diff_interface.py` | Two-panel Tkinter diff viewer with unified / side-by-side modes. |

---

## 7. Impact Analysis Guide

### 7.1 Replacing `pyperclip`

**Who uses it:** `obj-3d8fdd51`, `obj-75850ccd`, `obj-c96fd17d`, `obj-8fe32c41`

**Impact:** High. `multiclip.py` relies on `pyperclip.paste()` / `pyperclip.copy()` for the core copy-to-slot and paste-from-slot flows. `gui/history_panel.py` uses it for double-click clipboard copy. `diff_marker/diff_interface.py` uses it for paste-into-panel. Replacing requires updating 4 modules.

### 7.2 Replacing `pyautogui`

**Who uses it:** `obj-3d8fdd51` only

**Impact:** Medium. Only `multiclip.py` uses `pyautogui` for `Ctrl+C` simulation and fallback paste injection. The paste path already prefers `xdotool`, so `pyautogui` is mainly the copy-path. Could be replaced with `xdotool` entirely.

### 7.3 Replacing `pynput`

**Who uses it:** `obj-3d8fdd51` only

**Impact:** High but isolated. `pynput.keyboard.Listener` is the global hotkey backbone. Replacing it requires rewriting `_register_hotkeys()` entirely. Alternatives: `evdev`, `xlib`, or a window-manager-specific approach.

### 7.4 Modifying `ClipmanParser`

**Who depends on it:** `obj-3d8fdd51`, `obj-e059eede`, `obj-75850ccd`

**Impact:** Medium-high. Three modules consume `ClipEntry` objects. Any change to `ClipEntry` fields (e.g., adding metadata) requires updates in `multiclip.py` (`_transfer_clipman_to_og_slots`), `clipman_cli.py` (deploy logic), and `gui/history_panel.py` (display / copy logic).

### 7.5 Modifying Slot Persistence Format

**Who depends on it:** `obj-3d8fdd51` → `obj-983ee118` (clipboard_dict.json)

**Impact:** High. `load_slots()` and `save_slots()` in `multiclip.py` have custom backward-compatibility logic for old flat-dict formats. Changing the schema risks losing user data unless migration logic is preserved.

---

## 8. Navigation Cheat Sheet

| Goal | DSP Command |
|------|-------------|
| Find entity by file path | `python dsp-cli.py --root . find-by-source "shared/clipman_parser.py"` |
| See who imports a module | `python dsp-cli.py --root . get-recipients <uid>` |
| See what a module imports | `python dsp-cli.py --root . get-entity <uid>` |
| Trace dependency tree downward | `python dsp-cli.py --root . get-children <uid> --depth 2` |
| Trace dependency tree upward | `python dsp-cli.py --root . get-parents <uid> --depth 2` |
| Search by keyword | `python dsp-cli.py --root . search "toast"` |
| Check for cycles | `python dsp-cli.py --root . detect-cycles` |
| List all orphans | `python dsp-cli.py --root . get-orphans` |
| View full TOC | `python dsp-cli.py --root . read-toc` |

---

## 9. Persistence & Runtime Files

| File | Format | Written By | Read By | Notes |
|------|--------|------------|---------|-------|
| `clipboard_dict.json` | JSON | `multiclip.py` | `multiclip.py` | Auto-saved on every slot change and at exit via `atexit` + signal handlers. |
| `snippets.json` | JSON | `shared/snippets_manager.py`, `gui/main_window.py` | `shared/snippets_manager.py`, `gui/main_window.py` | Pre-seeded with tunnel config and proxy exports on first run. |
| `~/.cache/multiclip/deploy_queue.json` | JSON | `clipman_cli.py` | *(intended for multiclip)* | Deploy queue from curses browser; not currently consumed by main app. |
| `~/.multiclip/config.json` | JSON | `shared/config_manager.py` | `shared/config_manager.py` | Merged with hard-coded defaults on load. |
| `~/.multiclip/state.json` | JSON | `shared/config_manager.py` | `shared/config_manager.py` | Runtime state snapshot. |
| `/tmp/multiclip.lock` | flock | `multiclip.py` | `multiclip.py` | Kernel-level exclusive lock for single-instance enforcement. |

---

## 10. Known Constraints & Safety Notes

1. **Single-instance flock** is placed in `/tmp/multiclip.lock` so both `root` and `flintx` can see it. Running as `root` (e.g., `sudo`) while a user instance exists will block.
2. **Root + X11 paste reliability:** `multiclip.py` prefers `xdotool` over `pyautogui` when running as root because `pyautogui` hotkey injection is flaky under root on MX Linux.
3. **Clipman path fallback:** `ClipmanParser` hard-codes `/home/flintx/.cache/xfce4/clipman/textsrc` as a fallback when `SUDO_USER` resolution fails.
4. **No database:** All persistence is flat JSON. There is no migration framework beyond the inline dict-format handling in `load_slots()`.
5. **Diff module is self-contained:** `diff_marker/` only depends on `difflib` and `tkinter`. It can be extracted to a standalone package without modification.

---

*End of Data Structure Protocol output for the MultiClip project.*
