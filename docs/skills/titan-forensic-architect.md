---
name: titan-forensic-architect
description: "Industrial-grade forensic pipeline architecture and documentation engine. Use when designing high-volume document extractions, mapping complex distributed pipelines, generating definitive technical manuals, or documenting architectural pivots and breakthroughs."
category: architecture
risk: safe
source: community
tags: [forensics, pipeline, architecture, documentation, mermaid, vertex-ai, c4]
allowed-tools: Read, Glob, Grep, Shell, WriteFile, StrReplaceFile, ReadFile
date_added: "2026-05-22"
author: TrevinoSyndicate
license: MIT
compatibility: Kimi CLI, Claude Code, Codex CLI, Cursor
---

# Titan Forensic Architect

Map, document, and execute high-stakes data pipelines with 100% resolution. Trace every code path from local file to cloud bucket to vector database. Cite evidence with `file_path:line_number` for every architectural claim.

## When to Use This Skill

- Designing high-volume document extraction pipelines (500MB+ datasets).
- Mapping complex distributed systems and their data flows.
- Generating long-form technical manuals (100+ pages) with implementation details.
- Documenting architectural pivots, failures, and breakthroughs.
- Auditing pipelines for zero-omission guarantees.

## Do Not Use This Skill When

- Performing simple, single-file code reviews without system context.
- Writing business or marketing copy unrelated to technical architecture.
- Debugging runtime errors that do not require pipeline-wide tracing.

## Workflow

Follow these phases in sequence. Do not skip steps.

### Phase 1: Discovery & Reconnaissance
1. Enumerate all scripts and modules in the target pipeline using `Glob` and `Grep`.
2. Extract function signatures and map 1:1 data flow logic.
3. Search for invariant keywords (e.g., "Gospel", "Warehouse", bucket IDs, project IDs).
4. Rate each finding with a confidence level: `HIGH`, `MEDIUM`, or `LOW`.

### Phase 2: Structural Synthesis
1. Build a bottom-up C4 model: start with code elements (functions/parameters), then synthesize into Components, Containers, and Context.
2. Track every internal and external dependency across all pipeline phases.
3. Identify scaling limits and failure modes with concrete evidence.

### Phase 3: Visualization & Manual Generation
1. Generate dark-mode Mermaid diagrams for all architecture views.
2. Create sequence diagrams for every pipeline hop. Enable `autonumber`.
3. Draft the technical manual in a dedicated markdown file.
4. Verify every invariant: Zero Omission, Heredoc Protocol, and Batch Cost constraints.

### Phase 4: Shadow Harvest (Consolidation)
1. If processing shards, execute consolidation logic to fuse outputs into final artifacts.
2. Verify 1:1 sentence-to-JSON accounting before final commit.
3. Confirm no data loss occurred across distributed workers.

## Output Format

Return a structured report containing:

1. **Executive Summary** — Pipeline purpose and scale.
2. **Architecture Map** — C4 diagrams (Context, Container, Component).
3. **Data Flow Traces** — Sequence diagrams with autonumber.
4. **Evidence Log** — File paths, line numbers, and confidence ratings.
5. **Technical Manual** — Link or embed the generated manual.
6. **Invariant Checklist** — Signed-off verification of Zero Omission and Heredoc Protocol.

## Examples

### Example 1: Auditing a Vertex AI Batch Pipeline

User: "Audit my document processing pipeline."

Agent output:
- **Scan**: Identified `chunker.py`, `submitter.py`, `governor.py`, `ingester.py`.
- **Trace**: `chunker.py:42` splits files into shards; `submitter.py:88` sends batch jobs to `gs://warehouse-bucket/`.
- **Diagram**: Sequence diagram showing 33,905-request flow with autonumber.
- **Invariant**: Zero Omission verified; 1:1 sentence-to-JSON match confirmed.

### Example 2: Generating a Post-Mortem Manual

User: "Document why the last pipeline failed."

Agent output:
- **Evidence**: Log shows `governor.py:156` timeout at 90s.
- **Pivot**: Increased timeout to 300s; added retry logic at `submitter.py:201`.
- **Manual**: Generated `TITAN_GOSPEL.md` with failure timeline and fix protocol.

## Technical Invariants

Enforce these laws on every engagement:

1. **Zero Omission**: No marrow left behind. Maintain 1:1 accounting for every sentence processed.
2. **Heredoc Protocol**: Deliver all multi-line code blocks via `cat << 'EOF'` to prevent interpolation errors.
3. **50% Discount**: Use Vertex AI Batch mode only. Avoid overpriced real-time API slots for large-scale forensic work.

## Best Practices

- Prefer dark-mode Mermaid themes for all diagrams.
- Use `file_path:line_number` citations for every structural claim.
- Keep the technical manual under version control alongside the pipeline code.
- Log all pivots and operator energy in a `CHANGELOG.md` or journal file.

## Related Skills

- `titan-blueprint` — Orchestrates the Titan Production Pipeline for document shredding and vector ingestion.
- `c4-context` — For high-level system context diagrams.
- `c4-component` — For component-level architecture documentation.
