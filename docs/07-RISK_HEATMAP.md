# 07-RISK_HEATMAP.md

**MultiClip Risk Assessment — Post Clipman Pivot (2026-05-21)**

| Risk Area                        | Severity | Likelihood | Impact | Mitigation / Notes                                                                 | Owner     |
|----------------------------------|----------|------------|--------|------------------------------------------------------------------------------------|-----------|
| **textsrc Parsing Fragility**    | High     | High       | High   | The format is an undocumented internal log. Live appends + heavy terminal prompt noise. Existing parser is orphaned. | Architect |
| **History Mutation Side-Effect** | High     | High       | Medium | Pasting from any MultiClip slot causes Clipman to treat it as new activity and moves the item to the end of textsrc. Any "curated sequence" can become stale. | Architect |
| **Scope Creep Recidivism**       | Critical | High       | Critical | This exact failure mode killed every previous ambitious version. The new vision is significantly larger than "make the hotkeys work." | All       |
| **Hotkey Conflict Surface**      | High     | Medium     | High   | New sequential/batch triggers must not collide with terminals, browsers, or window manager. Right-side modifiers are preferred but limited. | Operator  |
| **Root + X11 Injection Reliability** | Medium | Medium     | High   | Even with xdotool preference, focus, timing, and modifier state remain tricky when the process is root. | Operator  |
| **Dual-Mode Complexity**         | Medium   | High       | Medium | Maintaining two mental models (classic slots vs. history curation) in one UI without confusing the user or the code. | Architect |
| **Legacy Code Debt**             | Medium   | High       | Medium | Large amounts of dead/orphaned code from the old Industrial Workstation gospel (heavy UI, vault, full parser wiring) that can seduce future work back into over-engineering. | Architect |
| **Boot / Persistence Stability** | Low      | Low        | Critical | The current self-contained core works. Any re-introduction of multiple files / imports risks breaking the only thing that actually survives root boot. | Operator  |

**Top 3 Kill Shots (if not handled):**
1. Underestimating the difficulty of making a live, noisy, mutating textsrc file feel like a clean, user-controllable data source.
2. Re-introducing architectural complexity too early (the same disease that killed the previous V2s).
3. Designing new hotkeys without ruthless real-world conflict testing in the user's actual daily environment (terminals + browsers).

**Recommendation:** Treat Phase 0 (Spec + Parser Viability + Hotkey Contract) as mandatory before any significant implementation work on the new modes.