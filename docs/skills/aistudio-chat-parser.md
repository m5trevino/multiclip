---
name: aistudio-chat-parser
description: "Extracts and transforms Gemini AI Studio chat exports into structured Markdown and interactive HTML transcripts. Supports granular message selection, staggered bubble views, and session directory management. Use when processing AI Studio JSON exports or managing chat archives."
type: core
category: development
risk: safe
tags: "[parsing, gemini, aistudio, chat-logs, archive]"
date_added: "2026-05-18"
allowed-tools: "*"
---

# aistudio-chat-parser

## Purpose

Extracts high-precision signal from Gemini AI Studio JSON exports (`chunkedPrompt` structure) and transforms it into human-readable Markdown and interactive, feature-rich HTML transcripts.

## When to Use This Skill

- When the user provides an AI Studio export file (handles files with **capital letters**, **spaces**, and **no file extension**).
- When the user wants to convert chat logs into human-readable Markdown or HTML.
- When the user needs an interactive "Bubble View" for chat review.
- When managing a local session archive that needs directory renaming or signal extraction.

## Setup

The skill relies on the `scripts/parse_aistudio.py` utility. It is filename-agnostic and uses internal JSON verification (`chunkedPrompt`) to identify valid exports.

```bash
# Basic usage
python3 scripts/parse_aistudio.py path/to/aistudio_export.json
```

## Core Patterns

### 1. Multi-Format Transformation
Converts raw JSON into three primary outputs:
- **`transcript.md`**: High-signal text version with ASCII separators.
- **`transcript.html`**: Interactive bubble view with selection UI.
- **`_standard_report.md`**: Heuristic signal extraction (VI/JE/IE) for the Peacock pipeline.

### 2. Staggered Bubble View (HTML)
The HTML output enforces a staggered, alternating layout:
- **Left Side**: User entries with curly brace { } styling.
- **Right Side**: Bot responses with symmetric curly brace styling.
- **No Center Line**: Clean visual separation without grid lines.
- **Checkbox Selection**: Every message has a checkbox for granular copying or exporting.

### 3. Session Management HUD
A dedicated dashboard view (`manager.html`) provides:
- **Session ID Mapping**: Links session hashes to descriptions.
- **Physical Renaming**: Inline field to rename the directory on disk.
- **Telemetry**: Records a "View Log" in `localStorage` to track review status.

## Common Mistakes

### [CRITICAL] Mismatching Export Format
Wrong:
```json
// Trying to parse a Claude or ChatGPT export with this script
{ "chat_messages": [...] } 
```
Correct:
```json
// Ensure the JSON contains the AI Studio chunkedPrompt key
{ "chunkedPrompt": { "chunks": [...] } }
```
The script will flinch if the root key is missing.

### [HIGH] Corrupting Directory Links
Wrong:
```python
# Renaming a directory without updating the central registry
os.rename(old_path, new_path)
```
Correct:
```python
# Use the internal update_registry() call to keep the HUD in sync
rename_and_register(session_id, new_name)
```

## References

- [HTML Template Guide](references/html-template-guide.md)
- [SVG Asset Definitions](references/svg-assets.md)
