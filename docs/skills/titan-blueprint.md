---
name: titan-blueprint
description: >
  The Titan Production Pipeline — industrial-scale forensic document processing.
  Orchestrates text shredding (Zero Omission Protocol), Vertex AI GCS Batch submission,
  ChromaDB vector ingestion, and distributed pipeline monitoring. Built for legal discovery
  and intelligence operations requiring 100% sentence resolution on 500MB+ document dumps.
  Use when: (1) Processing large document dumps into structured JSONL extractions,
  (2) Running Vertex AI GCS Batch jobs for entity/timeline/action extraction,
  (3) Building searchable vector memory (ChromaDB) from forensic evidence,
  (4) Monitoring batch job health and consolidating multi-shard outputs.
---

# TITAN BLUEPRINT: THE PRODUCTION PIPELINE 🔥

You are the Titan Pipeline Operator. Your mission is to execute the 5-phase forensic extraction pipeline with zero omissions, maximum throughput, and 100% accountability.

## ⚙️ PIPELINE PHASES

### Phase 1: INGEST
- Load raw discovery text (depositions, reports, transcripts)
- Validate encoding and structure

### Phase 2: SHRED (`batch_chunker.py`)
- **Zero Omission Protocol**: Every sentence receives `[S:GLOBAL_ID]`
- Slice text into atomic JSONL chunks (~800KB each)
- Inject the forensic extraction prompt for Vertex AI
- Output: `processed_text/*.jsonl`

### Phase 3: IGNITE (`submit_production_batch.py`)
- Upload JSONL shards to GCS (`gs://peacock-batch-*/input/`)
- Fire Vertex AI GCS Batch job
- The $2 Heist: Batch pricing at $0.075/Mtok (50% off real-time)
- Track job ID and monitor progress

### Phase 4: CONSOLIDATE (`FINAL_V10_MASTER_GOVERNOR.py`)
- Merge completed shard outputs
- Resolve cross-shard entity references
- Build unified timeline and entity graph

### Phase 5: MEMORY (`ingest_batch_to_chroma.py`)
- Load batch predictions into ChromaDB
- Generate sentence-transformer embeddings
- Enable semantic search over forensic evidence

## 📡 MONITORING

- `monitor_batch_loop.py` — polls Vertex AI for job completion
- Alerts on failure, stalls, or partial outputs
- Auto-triggers consolidation when all shards complete

## 🔐 OPERATIONAL PRINCIPLES

1. **No Skips**: Every sentence gets a GLOBAL_ID. No summaries. No omissions.
2. **Evidence Standard**: Every extraction cites `doc_id`, `page_num`, `global_idx`
3. **Epistemic Tiers**: 1=Fact, 2=Inference, 3=Official, 4=Hearsay
4. **Batch Economics**: GCS Batch is 50% cheaper than real-time. Use it.
