---
name: peacock-memory
description: >
  Master semantic memory system for FlintX's 1,385 chat archive across 
  claude/, chatgpt/, and aistudio/ directories. Integrates with Peacock 
  Engine V2 (localhost:3099) for key rotation, domain triage, and RAG 
  synthesis. Supports hybrid RRF search, embryonic idea mining, and 
  30+ project intelligence. Activate when user asks about chat history, 
  past projects, idea recovery, or memory search.
---

# PEACOCK MEMORY SKILL v2.0

## SYSTEM ARCHITECTURE

### Data Sources
- **Primary**: `/home/flintx/ai-chats/` with subdirectories:
  - `claude/all-logs-clean/` (historical Claude conversations)
  - `chatgpt/all-logs-clean/` (historical ChatGPT conversations)  
  - `aistudio/all-logs-clean/` (Gemini AI Studio, 25 accounts, branched)
- **Format**: Custom ASCII-bordered markdown (┎━─━┒ headers)
- **Total**: ~290MB, ~150M tokens, 1,385 files

### Peacock Engine Integration
- **Endpoint**: `http://localhost:3099/v1/strike` (Precision)
- **Endpoint**: `http://localhost:3099/v1/payload-strike` (Heavy context)
- **Key Pools**: 16 Groq keys, 3 Google Tier 1 keys (auto-rotated via Peacock)
- **Rescue Protocol**: 5-level parser for malformed responses

### The Vault System (Domain Routing)

| Vault | Contents | Collection Name |
|-------|----------|-----------------|
| **tech_vault** | Peacock, Social Lube, code, architecture, Linux, scripts | `tech_vault` |
| **case_files_vault** | True crime, investigations, legal analysis | `case_files_vault` |
| **personal_vault** | Spiritual, family, goals, personal history | `personal_vault` |
| **seed_vault** | Embryonic ideas, dormant projects, pivots, unassigned | `seed_vault` |

### Hybrid Search (RRF)
- **Semantic**: ChromaDB vector similarity (Gemini Embeddings via Peacock)
- **Keyword**: BM25 full-text (SQLite FTS5)
- **Metadata**: Structured filters (project, date, platform, maturity, branch)
- **Fusion**: Reciprocal Rank Fusion (k=60) across all signals

### Idea Mining Pipeline
During ingestion, every chunk analyzed for:
- **Maturity**: embryonic → exploring → committed → abandoned → completed → uncertain
- **Cross-project links**: Which projects reference which ideas
- **Branch detection**: Gemini main vs branch-2, branch-3, etc.
- **Resolution status**: Follow-up required vs. decided vs. implemented

## OPERATIONAL WORKFLOWS

### Workflow 1: Ingestion (Parallelized, Resumable)

Parse (ASCII regex) → Triage (Peacock strike) → Embed (3-key rotation)
→ Enrich (idea mining) → Route (correct vault) → Index (Chroma + BM25 + SQLite)
plain
Copy


### Workflow 2: Query (Real-time Hybrid)

User query → Expand synonyms → Hybrid retrieve (RRF: semantic + keyword + metadata)
→ [Optional] Peacock synthesize (Groq-16 rotation) → Cited response
plain
Copy


### Workflow 3: Idea Archaeology (Deep Analysis)

Scan seed_vault → Cluster embryonic ideas → Cross-reference with tech_vault
→ Detect abandoned gems → Resurrection candidates → Peacock validation → Report
plain
Copy


## YOUR CAPABILITIES

You have access to these tools in `scripts/`:

| Tool | Purpose | CLI Usage |
|------|---------|-----------|
| `vault_manager.py` | Full ingestion with checkpointing | `python vault_manager.py init [max_files]` |
| `vault_manager.py status` | Show ingestion progress | `python vault_manager.py status` |
| `query_engine.py` | Hybrid RRF search + synthesis | `python query_engine.py "query" --synthesize` |

## RESPONSE PROTOCOLS

When user asks about their chat history:

1. **ALWAYS cite sources**: [aistudio/dark-room-v3.md, Entry #042], [claude/2025-06-14.md, Entry #007]
2. **ALWAYS note maturity**: If idea is embryonic vs. implemented vs. abandoned
3. **ALWAYS surface contradictions**: If user said X then later Y in different chats
4. **ALWAYS check branches**: For Gemini, note if from main or branch-N
5. **ALWAYS respect Peacock integration**: Use `/v1/strike` for classification/synthesis

## EXAMPLE QUERIES

User: "What did I build with React?"
→ Use query_engine.py with RRF, filter tech_vault, synthesize via Peacock Groq

User: "Show me abandoned ideas about Peacock"
→ Query seed_vault + tech_vault for maturity=abandoned, project=peacock

User: "Am I ready to ship Social Lube?"
→ Archaeology: scan tech_vault for social-lube, check for unresolved TODOs, embryonic features

User: "What about that voice control thing I mentioned?"
→ Fuzzy search "voice" across all vaults, note if embryonic/unresolved in seed_vault

---

## BLOOD OATH (Skill Rules)

1. **Zero Generic RAG**: Never suggest "just use LangChain" or standard tutorials
2. **Peacock First**: Always attempt to use localhost:3099 before falling back to local models
3. **Cite Obsessively**: Every claim must link to [file, entry_number]
4. **Branch Aware**: Gemini branches are parallel thought tracks, not duplicates — surface them
5. **Idea Lifecycle Respect**: Distinguish "mentioned once in seed_vault" from "committed in tech_vault"
6. **Resume Capability**: Ingestion can pause/resume — respect checkpoint file
