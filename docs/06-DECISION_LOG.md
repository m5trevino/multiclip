# 06-DECISION_LOG.md

**Major Decisions in the MultiClip Lineage**

### 2026-05-21 — The Clipman Pivot (Current Session)
**Decision:** The primary value of MultiClip is no longer "30 reliable manual slots."  
It is now to act as a **curator and deterministic playback engine on top of the user's raw XFCE Clipman history**.

- Two explicit modes required (Classic + Clipman History).
- Users must be able to manually order/sequence items from the history.
- Sequential walk and batch paste from user-curated sets are first-class features.
- This overrides the earlier "keep it stupid simple, no scope creep" constraint that guided the hotkey/root rehab.

**Status:** Accepted. This is the new north star.

### 2026-05-20/21 — Hotkey Rehab Success
**Decision:** Move from `keyboard` library + mixed/Win-key hotkeys to raw `pynput` Listener with explicit left/right modifier tracking.

**Rationale:** The original hotkey approach was fundamentally unreliable under root on this MX Linux machine.

**Outcome:** LCtrl+LAlt copy and RCtrl+RAlt paste now work reliably (verified in live testing).

### 2026-05-20 — Survival Fork
**Decision:** During the reliability crisis, deliberately cut the project down to a self-contained single file (`multiclip.py`) and abandon the old multi-file "Industrial Workstation" architecture (heavy UI package, full manager, vault integration, etc.).

**Rationale:** The only thing that mattered was getting something that would actually start as root on boot with working global hotkeys.

**Consequence:** Much of the old gospel code became orphaned. This created technical debt but bought survival.

### Earlier (Gospel Era)
**Decision:** Build a "high-density Industrial Workstation" with 30 slots, full Clipman parser as core infrastructure, snippet vault, terminal-aware injection, and dense custom UI.

**Outcome:** Multiple versions died from scope creep, import hell, and hotkey unreliability (especially anything involving the Super/Win key).

---

**Pattern Observed:** Every time the project chased the full ambitious vision without a brutally stable foundation, it collapsed. The most recent rehab proved the opposite approach works (cut ruthlessly to what actually boots, then iterate).

The current challenge is whether the team can evolve the stabilized patient into the much more ambitious Clipman-history engine without re-contracting the old disease.