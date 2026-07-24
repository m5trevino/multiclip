# 00-EXECUTIVE_OVERVIEW.md

**MultiClip — Current State (Post-Rehab + Clipman Pivot)**

**Status as of 2026-05-21:** The project is in a transitional state after a major directional pivot.

## Executive Reality

MultiClip is a clipboard management tool for MX Linux (XFCE + sysVinit) that must run reliably as root on boot to own global hotkeys.

After multiple failed "V2 Industrial Workstation" attempts that died from scope creep and hotkey unreliability under root, a focused rehab stabilized a minimal, working core:

- 30 slots with simple JSON persistence
- Reliable Left Ctrl+Left Alt + 1-0 for copy
- Reliable Right Ctrl+Right Alt + 1-0 for paste (using raw pynput + xdotool-first injection)
- Self-contained single-file implementation for boot stability

This core currently works.

## The New Mandate (The Real Goal)

The user has now made it clear that the original "30 reliable slots" was never the endgame.

The actual objective is to turn MultiClip into a powerful **organizer and sequencer on top of XFCE Clipman's history** (`~/.cache/xfce4/clipman/textsrc`).

### Two-Mode Vision
1. **Classic Mode** — The existing 30-slot system (kept for quick manual capture).
2. **Clipman History Mode** — Browse the raw Clipman history, curate/organize entries into custom sequences or selections, then drive sophisticated playback:
   - Sequential paste (walk a user-defined order with one trigger)
   - Batch paste (paste a user-selected subset in exact selection order)

Clipman `textsrc` becomes the primary data lake. The classic slots become a secondary scratchpad.

## Current Technical State

**Living Code (High Confidence):**
- `multiclip.py` — The only version known to boot as root with correct L/R modifier behavior and working paste injection.
- Basic working paste path that prefers `xdotool` (more reliable under root).

**Orphaned / Historical Assets:**
- `shared/clipman_parser.py` — Existing parser logic (state-machine for escaped semicolons). Never integrated into the current working core.
- `gui/main_window.py` + dense SlotDisplay — The visual language the user still prefers from the old gospel era.
- Full "Industrial Workstation" architecture (heavy UI, Vault, full parser as core) — Largely abandoned during the reliability rehab.

**Major Open Risks:**
- Deep integration with a live, undocumented, constantly-appending internal log format (`textsrc`).
- History mutation side-effect (pasting from MultiClip moves items to the end of Clipman's history).
- Hotkey design for the new sequential/batch features without re-introducing conflicts.
- Avoiding the exact scope creep that killed every previous ambitious version.

## Strategic Situation

The project successfully performed emergency surgery to stabilize the patient (root boot + reliable hotkeys).

The user is now asking the stabilized patient to perform open-heart surgery on itself so it can become a general-purpose history curation and sequencing engine.

This is a significant re-architecture, not an incremental feature.

**Next logical move:** Produce a clean, authoritative spec + phased construction plan (already in progress via Blueprint) before writing any significant new code.

---

*This document reflects ground truth as of the latest conversation, not aspirational gospel from earlier attempts.*