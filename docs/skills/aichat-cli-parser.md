---
name: aichat-cli-parser
description: "Parses Kimi CLI and Gemini CLI chat session logs into structured Markdown archives. Extracts conversation sets, code blocks, attachments, thinking blocks, and tool calls with standardized divider formatting. Use when archiving AI chat sessions or converting CLI logs to readable formats."
type: core
category: development
risk: safe
tags: "[parsing, kimi, gemini, cli, chat-logs, archive, markdown]"
date_added: "2026-05-21"
allowed-tools: "*"
---

# aichat-cli-parser

## Purpose

Parses AI CLI session logs (Kimi and Gemini) into structured, human-readable Markdown with standardized dividers and asset extraction.

## When to Use This Skill

- When the user wants to archive or parse Kimi CLI session files
- When the user wants to archive or parse Gemini CLI `session-*.jsonl` files
- When converting raw CLI chat logs into structured Markdown for review
- When extracting code blocks, attachments, thinking blocks, or tool calls from sessions
- When preparing chat logs for the ChatLog Reader app or other consumers

## Supported Formats

| Source | Input Files | Output Dir |
|--------|-------------|------------|
| **Gemini CLI (current)** | `session-*.jsonl` — one JSON object per line | `~/save-aichats.com-gemini/<session_name>/` |
| **Gemini CLI (legacy)** | `session-*.json` — pretty-printed JSON with `messages[]` array | `~/save-aichats.com-gemini/<session_name>/` |
| **Kimi CLI** | `context.jsonl` / `context_1.jsonl` + `wire.jsonl` (in session dir) | `~/save-aichats.com-kimi/<session_name>/` |

The Gemini parser **auto-detects** both the JSONL and wrapped-JSON formats. You don't need to tell it which one you're using.

## Setup

The skill ships with two parser scripts in `scripts/`:

```bash
# Parse a Gemini CLI session
python3 scripts/parse_gemini.py ~/.gemini/tmp/sessions/session-2026-05-20T12-42-50a29dae.jsonl

# Parse a Kimi CLI session directory
python3 scripts/parse_kimi.py ~/.kimi/sessions/<session_uuid>/<thread_uuid>/
```

Both scripts accept an optional `--outdir` flag to override the default output location.

## Output Files

Every parsed session produces 5 Markdown files:

| File | Contents |
|------|----------|
| `CHAT_SETS.md` | Paired user/bot conversations with divider separators |
| `CODE_BLOCKS.md` | All fenced code blocks extracted, grouped by set |
| `ATTACHMENTS.md` | Image paths, clipboard refs, and file attachments |
| `THINKING.md` | Model reasoning / thinking blocks |
| `TOOLS.md` | Tool call summaries with arguments and outputs |

## Divider Format Standard

The parsers use a consistent divider system for downstream consumers:

- **User section:** `▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰`
- **Bot section:** `▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄▀▄`
- **Code/Image block:** `⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘`

## Core Patterns

### 1. Auto-Detecting Session Type
The parser scripts are **separate** — call `parse_gemini.py` for Gemini JSONL files and `parse_kimi.py` for Kimi session directories. They do not auto-detect format; you must choose the correct parser.

### 2. Default Archive Layout
```
~/save-aichats.com-gemini/
  session-2026-05-20T12-42-50a29dae/
    CHAT_SETS.md
    CODE_BLOCKS.md
    ATTACHMENTS.md
    THINKING.md
    TOOLS.md

~/save-aichats.com-kimi/
  9fa8f39d-c7a0-4ab4-a981-82b4c305d425/
    CHAT_SETS.md
    CODE_BLOCKS.md
    ATTACHMENTS.md
    THINKING.md
    TOOLS.md
```

### 3. Batch Processing
To parse all sessions in a directory:

```bash
# Gemini — all session files
for f in ~/.gemini/tmp/sessions/session-*.jsonl; do
    python3 scripts/parse_gemini.py "$f"
done

# Kimi — all session directories
for d in ~/.kimi/sessions/*/*; do
    [ -d "$d" ] && python3 scripts/parse_kimi.py "$d"
done
```

## Common Mistakes

### [CRITICAL] Wrong Parser for Wrong Format
Wrong:
```bash
# Gemini file passed to Kimi parser
python3 scripts/parse_kimi.py session-2026-05-20.jsonl
```
Correct:
```bash
python3 scripts/parse_gemini.py session-2026-05-20.jsonl
```

### [HIGH] Missing context_1.jsonl in Kimi Session
Kimi sessions require the full session directory, not just one file. The parser looks for `context_1.jsonl` and optionally `wire.jsonl` inside the directory.

Wrong:
```bash
python3 scripts/parse_kimi.py ~/.kimi/sessions/e84335/wire.jsonl
```
Correct:
```bash
python3 scripts/parse_kimi.py ~/.kimi/sessions/e84335/9fa8f39d-c7a0-4ab4-a981-82b4c305d425/
```

## References

- `scripts/parse_gemini.py` — Gemini CLI JSONL parser
- `scripts/parse_kimi.py` — Kimi CLI session directory parser
