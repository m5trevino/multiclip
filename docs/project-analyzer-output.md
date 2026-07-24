# Project Analysis Report: MultiClip V2

## 1. Project Overview

MultiClip V2 is an advanced, industrial-grade clipboard manager designed for Linux (specifically MX Linux / Debian-based distributions running XFCE). Its primary purpose is to supercharge the standard clipboard experience by providing 30 persistent "slots" for copy/paste operations, deep integration with the XFCE Clipman clipboard history, and multiple operational modes (Multiclip, Orderly, Vault, Sequential, and Diff-Marker). The application targets power users, developers, and content creators who need to manage large volumes of clipboard data efficiently without losing context.

The project was built iteratively with a strong focus on root-user compatibility, hotkey-driven workflows, and integration with the existing XFCE Clipman plugin. It runs as a background daemon with both a tkinter GUI and global system hotkeys, enabling users to copy content into numbered slots using left-side modifier combos (LCtrl+LAlt+digit) and paste from those slots using right-side modifier combos (RCtrl+RAlt+digit).

## 2. Tech Stack

| Category | Technologies |
| :--- | :--- |
| **Languages** | Python 3 |
| **GUI Framework** | tkinter (standard library) |
| **Clipboard Access** | pyperclip, pyautogui |
| **Global Hotkeys** | pynput |
| **System Integration** | xdotool, notify-send, fcntl (single-instance guard) |
| **Data Persistence** | JSON flat files (clipboard_dict.json, snippets.json) |
| **Diff Engine** | Python difflib (standard library) |
| **Infrastructure** | SysVinit service, systemd service file (legacy), bash scripts |
| **Testing** | Manual test scripts (test_hotkeys.py, test_clipman_parser.py, etc.) |
| **Build Tools** | Python venv, pip, bash setup scripts |
| **OS Target** | Linux (MX Linux / Debian), X11, XFCE4 |

## 3. Core Features

- **30-Slot Workbench**: Users can copy content into 30 numbered clipboard slots using LCtrl+LAlt+digit hotkeys, and paste from them using RCtrl+RAlt+digit hotkeys. Slots persist across reboots via `clipboard_dict.json`.
- **XFCE Clipman Integration**: Parses `~/.cache/xfce4/clipman/textsrc` to display the user's full clipboard history in a paginated panel (50 items per page). Supports live polling (every 3 seconds) to detect new clipboard entries without restarting.
- **Smart Transfer from History**: Users can select multiple entries from Clipman history and transfer them to Workbench slots either as a batch (one entry per slot) or joined into a single slot. Includes slot-overflow handling with a user prompt.
- **Persistent Snippets**: A bottom-left Snippets panel stores up to 8 quick-access text snippets that survive restarts. A separate Snippet Vault (right panel) holds 10 additional persistent items with hotkey support.
- **Orderly Mode (Partially Implemented)**: Designed for sequential copy/paste workflows with independent copy and paste cursors, FIFO/LIFO sub-modes, and circular buffer behavior when all 30 slots are full.
- **Diff-Marker**: A built-in text comparison tool using Python's `difflib` with side-by-side and unified diff views, color-coded highlighting, and integration with clipboard slots.
- **System Notifications**: Every copy/paste action triggers a detailed `notify-send` toast showing the action type, slot number, and a content preview.
- **Single-Instance Guard**: Uses `fcntl.flock` on `/tmp/multiclip.lock` to prevent multiple instances from running simultaneously.
- **Terminal Awareness**: Detects active terminal windows via `xdotool`/`xprop` and uses `Ctrl+Shift+V` for pasting in terminals instead of `Ctrl+V`.
- **Boot Service**: Installs as a SysVinit service (`/etc/init.d/multiclip`) that starts automatically on boot, running as root with X11 cookie copying for display access.

## 4. REST Services & Endpoints

This project is a **desktop GUI application with no network layer**. It does not expose any REST APIs, HTTP endpoints, or web services. All functionality is local-only, operating through:
- Global keyboard listeners (pynput)
- tkinter GUI event loops
- File-based data persistence (JSON)
- System clipboard and X11 integration

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| N/A | N/A | No REST endpoints — purely local desktop application |

## 5. Project Structure

```text
/home/flintx/multiclip/
├── multiclip.py                    # Main entry point — MultiClipV2 class, hotkeys, clipboard logic
├── clipman_cli.py                  # Curses-based CLI browser for clipman history (standalone)
├── ordely.py                       # Orderly mode manager — sequential copy/paste workflow logic
├── snippers-view.py                # Snippers command library GUI (category tree, search, variable substitution)
├── snippers-save.py                # Snippet save utility (referenced, not fully explored)
├── gui/
│   ├── main_window.py              # tkinter MainWindow — 30-slot workbench, clipman panel, snippets, vault, toasts
│   └── history_panel.py            # HistoryPanel widget — integrated clipman history with canvas scroll
├── shared/
│   ├── clipboard_manager.py        # ClipboardSlot & ClipboardManager — slot storage abstraction
│   ├── clipman_parser.py           # ClipmanParser & ClipEntry — parses XFCE clipman textsrc file
│   ├── config_manager.py           # ConfigManager — JSON config/state/snippets persistence (~/.multiclip/)
│   └── snippets_manager.py         # SnippetVault — lean 20-slot snippet storage with defaults
├── diff_marker/
│   ├── __init__.py                 # Module exports (DiffManager, DiffInterface, DiffResult, etc.)
│   ├── diff_manager.py             # Core diff calculation using difflib.SequenceMatcher
│   ├── diff_interface.py           # tkinter UI for two-panel diff comparison
│   └── diff_types.py               # DiffType enum, DiffLine & DiffResult dataclasses
├── docs/                           # Project documentation
│   ├── 00-EXECUTIVE_OVERVIEW.md
│   ├── CLIPMAN_INTEGRATION_SPEC.md
│   ├── MULTICLIP_CLIPMAN_IMPLEMENTATION_PLAN.md
│   ├── multiclip-v3-spec.md        # V3 feature specification (boot fixes, orderly mode, UI renames)
│   └── ... (additional docs)
├── analysis/                       # 4-stage analysis documents (spark, falcon, eagle, hawk)
├── standard-skill/                 # Peacock standard skill outputs from chat sessions
├── *.sh                            # Setup, launch, and service scripts (see below)
├── multiclip.service               # systemd service unit file (legacy, mostly replaced by SysVinit)
├── multiclip-init.d                # SysVinit init script with X11 cookie copying
├── requirements.txt                # Python dependencies (pyperclip, pyautogui, pynput)
├── clipboard_dict.json             # Runtime slot persistence (30 slots)
├── snippets.json                   # Snippet vault persistence
└── test_*.py                       # Various diagnostic and manual test scripts
```

## 6. Architecture Summary

The project follows a **layered desktop application architecture** with clear separation between UI, business logic, and system integration:

- **Presentation Layer**: `gui/main_window.py` (dense tkinter workbench), `gui/history_panel.py` (scrollable history), `clipman_cli.py` (curses fallback), and `diff_marker/diff_interface.py` (diff UI). The main window uses a two-column layout: left column holds the 30-slot Workbench and Snippets; right column holds the Clipman History panel and Vault.
- **Application Layer**: `multiclip.py` serves as the application controller, wiring together hotkeys, slot persistence, the old GUI, and Clipman integration. It handles the global keyboard listener lifecycle and emergency save on exit.
- **Domain Layer**: `shared/clipboard_manager.py` (slot abstraction), `shared/clipman_parser.py` (history parsing), `ordely.py` (sequential workflow state machine), and `diff_marker/diff_manager.py` (text comparison engine).
- **Infrastructure Layer**: `shared/config_manager.py` (file I/O for config/state), shell scripts for service management, and direct system calls to `xdotool`, `notify-send`, and `xprop`.

The architecture is **modular but tightly coupled to the Linux/X11/XFCE environment**. There is no inversion-of-control container; wiring is done imperatively in `multiclip.py`.

## 7. Data Architecture & Models

- **Database**: None. All persistence is file-based JSON.
- **Key Data Stores**:
  - `clipboard_dict.json` — Stores the 30 Workbench slots as a JSON object `{ "slots": { "1": "content", ... } }`. Located in the project root.
  - `snippets.json` — Stores up to 20 snippet strings keyed by index. Located in the project root.
  - `~/.multiclip/config.json` — User configuration (hotkeys, GUI settings, behavior, terminal detection) managed by `ConfigManager`.
  - `~/.multiclip/state.json` — Runtime state snapshots.
  - `~/.cache/xfce4/clipman/textsrc` — **External read-only source**: XFCE Clipman's raw history file, parsed by `ClipmanParser`.
- **Key Entities**:
  - `ClipboardSlot` (`shared/clipboard_manager.py`): `id`, `content`, `order`, `timestamp`, `preview`.
  - `ClipEntry` (`shared/clipman_parser.py`): `id`, `content`, `preview`, `word_count`, `decoded_content`.
  - `DiffResult` / `DiffLine` (`diff_marker/diff_types.py`): Structured diff output with stats (additions, deletions, modifications).
  - `OrderlyState` (`ordely.py`): Tracks active flag, current slot, paste sequence, and paste index for orderly mode.

## 8. External Integrations

- **XFCE4 Clipman Plugin**: Reads the clipboard history file at `~/.cache/xfce4/clipman/textsrc`. This is the primary external dependency — MultiClip is designed to complement, not replace, Clipman.
- **X11 / Xorg**: Heavy reliance on X11 for window detection (`xdotool getactivewindow`, `xprop WM_CLASS`), paste injection (`xdotool key --clearmodifiers ctrl+v`), and display access (`DISPLAY=:0`, `.Xauthority`).
- **notify-send (libnotify)**: Desktop toast notifications for every copy/paste action, including the custom `chargers.png` icon.
- **SystemD (legacy)**: `multiclip.service` exists but is being phased out in favor of SysVinit on MX Linux.
- **SysVinit**: The primary service management mechanism. The init script copies the user's X11 cookie to `/tmp/.Xauthority_multiclip` so root can access the display.

## 9. CI/CD & DevOps

- **Pipeline**: No automated CI/CD pipeline exists. The project is manually deployed.
- **Containerization**: None. No Docker, Docker Compose, or container artifacts.
- **Deployment**:
  - `setup.sh` — Creates a Python virtual environment, installs dependencies, makes scripts executable, and creates a `.desktop` entry.
  - `install-multiclip-service.sh` — Installs the SysVinit service (`/etc/init.d/multiclip`), enables it at boot via `update-rc.d`, and sets up log files.
  - `multiclip-launcher.sh` — The launcher script referenced by the init script. Waits for X11, sets environment variables, and runs the Python app.
  - `fix-boot-duplication.sh` / `fix-boot-service.sh` — Maintenance scripts to resolve service conflicts and boot duplication issues.
- **Service Management**:
  - Start: `sudo /etc/init.d/multiclip start`
  - Stop: `sudo /etc/init.d/multiclip stop`
  - Logs: `sudo tail -f /var/log/multiclip.log`

## 10. Testing Strategy

- **Frameworks**: No formal test framework (no pytest, unittest, or CI test runner). Testing is entirely manual and diagnostic.
- **Test Scripts**:
  - `test_hotkeys.py` — Manual hotkey verification with `pynput.GlobalHotKeys`. Verifies LCtrl+LAlt and RCtrl+RAlt combos.
  - `test_hotkeys_v2.py` — Extended hotkey tests.
  - `test_clipman_parser.py` — Diagnostic script that runs the parser against the live `textsrc` file and prints preview statistics.
  - `test_clipboard_monitor.py` — Clipboard monitoring diagnostics.
  - `test_clipman_integration.py` — Integration tests for the Clipman panel.
  - `test_modifiers.py` — Modifier key testing.
  - `test_unified.py` / `test_original.py` — Additional manual verification scripts.
- **Coverage**: Low formal coverage. Quality is ensured through manual end-to-end testing on the target MX Linux environment.

## 11. Other Relevant Information

- **Build/Run Instructions**:
  1. `cd /home/flintx/multiclip`
  2. `./setup.sh` (creates venv and installs deps)
  3. `./start-multiclip.sh` or `sudo /etc/init.d/multiclip start`
  4. Alternatively: `.venv/bin/python multiclip.py`
- **Environment Variables**:
  - `DISPLAY=:0`
  - `XAUTHORITY=/home/flintx/.Xauthority` (or `/tmp/.Xauthority_multiclip` when running as root)
  - `XDG_RUNTIME_DIR=/run/user/1000`
  - `HOME=/home/flintx`
- **Key Files & Permissions**:
  - The app is designed to run as **root** for global hotkey reliability, but accesses the desktop user's X11 session via copied cookies.
  - `clipboard_dict.json` and `snippets.json` must be writable by the runtime user.
  - `/tmp/multiclip.lock` is used for the single-instance flock guard.
- **Project Evolution**:
  - The project has gone through multiple iterations (V1 → V2 → V3 spec). 
  - `multiclip.py.bak.*` and `requirements.txt.bak.*` files indicate iterative development with rollback points.
  - The V3 spec (`multiclip-v3-spec.md`) outlines planned features: boot fixes, button renames ("Block Bundle", "1 slot per line"), Orderly mode wiring, visual transfer feedback, and snippet removal buttons.
- **Peacock Integration**: The project lives within the broader Peacock organization ecosystem. It uses the Peacock standard skill pipeline (chat transcripts are processed into structured journal/instruction entries in `standard-skill/`). Multiple UUID-named directories (`a1e09243-...`, `a938f4c9-...`, etc.) contain standard-skill artifacts from previous sessions.
