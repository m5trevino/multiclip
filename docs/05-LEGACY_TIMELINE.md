# 05-LEGACY_TIMELINE.md

**MultiClip Evolutionary Timeline (Condensed)**

**Phase 0 — Original Simple Version**
- Basic 1-9 / Ctrl+Shift hotkeys using `keyboard` + `pyautogui` + `pyperclip`.
- Worked for the user in daily life for a long time.

**Phase 1 — "Industrial Workstation" Ambition (Gospel Era)**
- Massive expansion: 30 slots, dense custom UI, full Clipman parser as core, snippet vault, orderly/sequential modes, Win+V triggers, heavy architecture.
- Multiple implementations attempted.
- Repeated deaths from:
  - Hotkey unreliability (especially anything with Super/Win key)
  - Import hell and missing pieces when running as root
  - Scope creep

**Phase 2 — The Rehab (Survival Surgery)**
- Focused exclusively on making something boot as root with reliable global hotkeys.
- Switched to raw `pynput` + explicit left/right tracking.
- Cut the system down to a single self-contained file.
- Made paste prefer `xdotool` for root reliability.
- Result: First version in a long time that actually works under the required constraints (root on MX sysVinit boot).

**Phase 3 — The Pivot (Current)**
- User reveals that the "30 reliable slots" was never the real destination.
- Real destination: Deep integration with Clipman `textsrc` as the primary data source.
- New required capabilities: Browse history, user curation into sequences, sequential playback, batch from selection.
- Classic 30-slot mode is now secondary ("keep what works").
- Massive new scope + significant new technical risks (live log parsing, history mutation, new hotkey surface).

**Current State:** We have a stabilized, narrow foundation. The user wants to build a much wider cathedral on top of it. The historical pattern suggests this is the most dangerous moment in the project's life.