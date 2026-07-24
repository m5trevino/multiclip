# DEV JOURNAL: MultiClip — 2026-05-26

**Project:** `/home/flintx/multiclip`  
**Platform:** MX Linux (XFCE + sysVinit)  
**Runtime Constraint:** Must boot and run reliably as `root` for global hotkey ownership  
**Current Status:** Post-Rehab stabilization + Clipman Pivot in progress  

---

## 🎯 Mission Objective

MultiClip started as a simple personal clipboard multiplier and evolved into a battle-hardened ** Industrial Workstation** for clipboard orchestration. The ultimate goal is not merely "30 reliable slots" — it is to turn MultiClip into a **deterministic curator and playback engine on top of the user's raw XFCE Clipman history** (`~/.cache/xfce4/clipman/textsrc`).

The user wants to browse their entire copy/paste history, selectively organize entries into custom sequences, and then drive sophisticated paste operations — sequential walk, batch from selection, and snippet vaulting — all without ever leaving the hotkey-centric workflow.

> *"The user is asking the stabilized patient to perform open-heart surgery on itself so it can become a general-purpose history curation and sequencing engine."*

---

## 🏗️ Architectural Evolution

### The Legacy — "The Gospel Era" (Phase 1)

The original vision was massive:
- **30-slot high-density grid** with custom sequencing
- **Full Clipman parser** as core infrastructure
- **Snippet Vault** with persistent hotkeys (`Win + Alt + 1-0`)
- **Terminal-aware paste engine** using `xdotool` to toggle `Ctrl+V` vs `Ctrl+Shift+V`
- **Dense custom UI** (`gui/main_window.py`) with industrial toast feedback
- **Win/Super-key triggers** for paste strikes

**Why it died (repeatedly):**
1. **Hotkey unreliability** — Anything involving the Super/Win key conflicted with XFCE WM and got stuck.
2. **Import hell** — Multi-file architecture with heavy UI packages failed to load when running as `root` on boot.
3. **Scope creep** — Every attempt chased the full cathedral before the foundation could hold weight.

Multiple implementations were attempted. All collapsed under the same disease.

### The Pivot — "Survival Surgery" (Phase 2 — The Rehab)

During the reliability crisis, the project was **ruthlessly cut** to a single self-contained file (`multiclip.py`). The only thing that mattered was getting something that would actually start as `root` on boot with working global hotkeys.

**Key changes:**
- Ditched the `keyboard` library for **raw `pynput` Listener** with explicit left/right modifier tracking.
- Switched hotkeys to **Left Ctrl + Left Alt + 1-0 (copy)** and **Right Ctrl + Right Alt + 1-0 (paste)**.
- Made paste prefer **`xdotool`** for root reliability.
- Added a **single-instance guard** (`fcntl.flock` on `/tmp/multiclip.lock`).
- Cut the system down to a **single-file, boot-stable core**.

**Result:** First version in a long time that actually works under the required constraints (root on MX sysVinit boot). The user could finally use it in daily life again.

> *The "Fuckin' Ugh" moment: Watching every ambitious V2 die because of Super-key stickiness and import failures at root boot. The user explicitly said: "I am on mx linux... it has to launch as sudo also."*

### The Current State — "The Clipman Pivot" (Phase 3)

**2026-05-21: The user reveals the true destination.**

The "30 reliable slots" was never the endgame. The real objective is deep integration with Clipman `textsrc` as the primary data lake:

- **Classic Mode** — Keep the 30-slot system as a secondary scratchpad (LCtrl+LAlt / RCtrl+RAlt remains sacred).
- **Clipman History Mode** — Browse the raw Clipman history, curate entries into custom sequences, and drive playback:
  - **Sequential paste** — Walk a user-defined order with one trigger.
  - **Batch paste** — Paste a user-selected subset in exact selection order.
- **Snippets** — Persistent reusable text parked in bottom-left slots.
- **Orderly Mode** — Auto-capture `Ctrl+C` into slots and paste sequentially (FIFO/LIFO).
- **Diff-Marker Mode** — Visual text comparison integrated as a 4th mode.

This directly overrides the earlier "keep it stupid simple, no scope creep" constraint that guided the rehab. It is the most dangerous moment in the project's life — the exact failure mode that killed every previous ambitious version is now being invited back in.

---

## 🧪 Technical Invariants & Rules

These are the ground truth laws governing MultiClip. Break them, and the system dies.

1. **ROOT IS NON-NEGOTIABLE**  
   Global keyboard hooks require root. The init.d service must launch as root. X11 auth must be handled (`~/.Xauthority` copied to `/tmp/.Xauthority_multiclip`).

2. **SINGLE-INSTANCE GUARD**  
   `fcntl.flock` on `/tmp/multiclip.lock`. No second instances allowed — this prevents the boot-duplication bug that once opened 2 instances at startup.

3. **LCtrl+LAlt = COPY, RCtrl+RAlt = PASTE**  
   The left/right modifier split is the only hotkey scheme that has survived real-world terminal and browser usage without conflicts.

4. **XDOTOOL-FIRST PASTE INJECTION**  
   When running as root, `xdotool` is more reliable than `pyautogui.typewrite` for paste operations. Terminal detection toggles `Ctrl+V` vs `Ctrl+Shift+V`.

5. **textsrc IS A LIVE, MUTATING, UNDOCUMENTED LOG**  
   Entries are semicolon-delimited with escapes (`\;`, `\n`, `\s`, `\t`). The file is constantly appended by Clipman. Pasting from MultiClip moves items to the end of the history. Any curated sequence can become stale.

6. **PROTECT THE WORKING CORE AT ALL COSTS**  
   New features must not break the existing hotkey + paste reliability. This is the lesson learned from every prior collapse.

7. **NO HALLUCINATION — ASK IF UNCLEAR**  
   The user explicitly demanded: "If anything is unclear, stop and ask. Do it right, even if it takes longer."

---

## 🔥 Feature Arsenal

### Classic 30-Slot Workbench
- 30 persistent slots with JSON storage (`clipboard_dict.json`)
- Numeric sequence ordering (1–30)
- Normalize button resets to default order
- Smart transfer fills empty slots first; warns when full with user choice of overwrite target

### Clipman History Panel
- Parses real `~/.cache/xfce4/clipman/textsrc` (handles root vs user home path fallback)
- Pagination: 50 items per page, only renders current page widgets
- Live refresh: polls textsrc every 3 seconds via `tk.after()`, only redraws on mtime change
- Double-click preview popup with Single/Show All modes and Prev/Next navigation

### Transfer Operations
- **Block Bundle** (formerly "Transfer as Batch") — each selected row gets its own OG slot
- **1 Slot Per Line** (formerly "Transfer as One Slot") — forces selected content into a single slot
- Manual slot selection mode — user clicks a workbench slot to set the starting fill position
- Visual transfer feedback — slow gold/green pulse on destination slot (~2 seconds)

### Snippets Vault
- 8 persistent snippet slots stored in `snippets.json`
- Add, edit, delete, save functionality
- Survives restarts
- Reserved space for future hotkeys

### Orderly Mode
- Auto-captures every `Ctrl+C` into workbench slots
- Paste cursor advances independently from copy cursor
- Wrap-around circular buffer when all 30 slots fill
- FIFO and LIFO sub-modes
- "Next paste slot" always highlighted in the workbench

### Diff-Marker Mode
- 4th mode added alongside MultiClip, Orderly, and Snippers
- Two-panel text input for comparison
- Side-by-side and unified diff views
- Color-coded highlighting (green insert, red delete, yellow replace)
- Load from and save to clipboard slots

### Boot & Service Infrastructure
- SysVinit service (`/etc/init.d/multiclip`) — systemd and XFCE autostart removed to fix duplication
- X11 cookie copy for root display access
- Init.d runlevel symlinks fixed from `K01` to `S03`
- Emergency save on `SIGINT` / `SIGTERM` via `atexit`

---

## 📡 Tactical Stack

| Layer | Technology | Role |
|---|---|---|
| **Language** | Python 3.11 | Core runtime |
| **UI Framework** | tkinter + ttk | All interface rendering |
| **Hotkey Capture** | `pynput` (raw Listener) | Global keyboard hooks with L/R modifier tracking |
| **Paste Injection** | `pyautogui` + `xdotool` | Clipboard pasting with terminal detection |
| **Clipboard I/O** | `pyperclip` | System clipboard read/write |
| **Data Source** | XFCE Clipman `textsrc` | Raw history log (semicolon-delimited, escaped) |
| **Persistence** | JSON (`clipboard_dict.json`, `snippets.json`) | Slot and snippet storage |
| **Parser** | Custom state-machine (`shared/clipman_parser.py`) | Splits on unescaped `;`, decodes `\n` / `\s` / `\t` |
| **Init System** | SysVinit (MX Linux) | Boot service — systemd intentionally removed |
| **Locking** | `fcntl.flock` | Single-instance kernel-level guard |

---

## 🚀 Future Recon

**Immediate (In Progress / Spec'd):**
- Fully wire Orderly mode (currently partially implemented)
- Complete FIFO/LIFO button wiring inside Clipman History panel
- Visual slot highlighting for "next paste" cursor
- Status bar queue info (`"Queue: 12 items | Next: Slot 05"`)
- Snippet removal via dedicated X button

**Short-Term:**
- Hotkeys for snippets, transfer, pagination
- Named sequences / multiple saved sequences
- Better search/filter in Clipman History
- Visual indicators showing which OG slots came from Clipman recently

**Long-Term / High-Risk:**
- Deeper intra-entry text selection (Listbox may become too limiting)
- Export / backup of curated sequences
- History mutation side-effect mitigation (or turning it into a feature)

**Top 3 Kill Shots to Avoid:**
1. Underestimating the difficulty of making a live, noisy, mutating `textsrc` file feel like a clean, user-controllable data source.
2. Re-introducing architectural complexity too early (the same disease that killed the previous V2s).
3. Designing new hotkeys without ruthless real-world conflict testing in the user's actual daily environment (terminals + browsers).

---

## 📓 Session Energy & Tone

The build energy has been **intense and pragmatic**. The user is a power user who knows exactly what they want but has been burned by previous over-engineering. Key tonal markers:

- **"NO CODE YET AT ALL!!!!!"** — The user enforced a strict vision-dump phase before any implementation.
- **"Keep it practical"** — This is a tool to work faster on other projects, not a big architecture project.
- **"Do it right, even if it takes longer"** — Quality over speed when ambiguity exists.
- **"I dont like the shift + the nuber because when i use the terminal and when i use the chrome browser it causes conflicts"** — Real-world daily driver constraints drive every decision.

The user has learned from past failures. The current approach is: stabilize ruthlessly, then evolve carefully. The danger is that the new vision is significantly larger than "make the hotkeys work." Whether the team can build the cathedral on the stabilized foundation without re-contracting the old disease is the defining question of this project's next chapter.

---

*Authored by dev-tech-journal skill | Analysis sourced from chat transcripts, git history, spec documents, and codebase archaeology.*
