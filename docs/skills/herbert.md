---
name: herbert
description: |
  Query the Peacock binding database to infer the correct UI component for any API endpoint.
  Given an HTTP method + path + intent, Herbert returns a structured prescription
  (component name, props, confidence score) and a human-readable explanation.
  Use whenever you need to choose or scaffold a UI for a backend endpoint.
license: MIT
allowed-tools:
  - Bash
  - Read
---

# Herbert — Peacock Binding Inference Agent

Query the Peacock semantic binding database and map API endpoints to concrete UI components.

## When to Use This Skill

Activate Herbert when you need to:

- **Pick a UI component** for a new API endpoint
- **Map an existing endpoint** to its ideal frontend representation
- **Batch-process** many endpoints at once (e.g. scaffolding a full page)
- **Explore available UI patterns** Peacock knows about
- **Generate props** for React/Vue components from API metadata

## Quick Reference

### Single Endpoint Prescription

```bash
cd /home/flintx/webapp-mapping
python3 herbert/herbert.py --intent FILE_SELECTION --path /apps/{id}/prebuilts --method POST
```

### Semantic Search (by description)

```bash
python3 herbert/herbert.py --intent FILE_SELECTION --text "grid checkbox" -n 5
```

### Batch Process Multiple Endpoints

```bash
python3 herbert/herbert.py --batch herbert/examples/batch.json
```

### List Supported Patterns

```bash
python3 herbert/herbert.py --patterns
```

### Raw JSON Output

```bash
python3 herbert/herbert.py --intent DEPLOYMENT --json
```

## Installation

1. Ensure the `herbert/` directory is in your project or PYTHONPATH.
2. No external dependencies beyond Python 3.8+ standard library.

## Prescription Structure

Herbert returns a JSON object like:

```json
{
  "status": "ok",
  "prescription": {
    "component": "FileSelectionGrid",
    "category": "FILE_SELECTION",
    "props": {
      "endpoint": "/apps/{id}/prebuilts",
      "method": "POST",
      "selectionMode": "multiple",
      "showCheckboxes": true,
      "layout": "grid",
      "itemName": "Prebuilts"
    },
    "description": "A selectable grid where users can multi-select items via checkboxes.",
    "match_type": "pattern",
    "confidence": 0.81
  },
  "source_binding": {
    "intent": "FILE_SELECTION",
    "method": "POST",
    "path": "/apps/{appId}/versions/{versionId}/prebuilts",
    "ui_invariant": "Multi-select Apps grid with checkbox state",
    "confidence": 0.81
  },
  "alternatives": [...]
}
```

## Python API

```python
from herbert.adapter import prescribe, batch_prescribe, explain_prescription

# Single endpoint
result = prescribe(
    intent="FILE_SELECTION",
    path="/missions",
    method="POST"
)
print(result["prescription"]["component"])  # "FileSelectionGrid"

# Batch
results = batch_prescribe([
    {"intent": "FILE_SELECTION", "path": "/missions", "method": "POST"},
    {"intent": "DEPLOYMENT",     "path": "/deploy",   "method": "POST"},
])

# Human-readable explanation
print(explain_prescription(result))
```

## React Integration

```jsx
import HerbertAdapter from "./herbert/HerbertAdapter";

<HerbertAdapter
  intent="FILE_SELECTION"
  path="/apps/{id}/prebuilts"
  method="POST"
  n={3}
/>
```

The adapter queries Peacock at render time and renders the correct component automatically.

## How It Works

1. **Query** → Herbert hits `https://peacock.save-aichats.com/search` (falls back to `http://127.0.0.1:7878`)
2. **Map** → `mapper.py` matches the `ui_invariant` against known patterns
3. **Prescribe** → Returns a component name, props, and confidence score
4. **Render** → `HerbertAdapter.jsx` renders the matching component

## Confidence Thresholding

Use `--min-confidence 0.7` to only accept high-confidence matches:

```bash
python3 herbert/herbert.py --intent FILE_SELECTION --path /upload --method POST --min-confidence 0.7
```

If no result meets the threshold, Herbert returns the best available match with a warning.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `No results from Peacock` | Check network or start local Peacock on `:7878` |
| Low confidence | Broaden intent or use semantic `--text` search |
| Component not found | Run `--patterns` to see supported mappings |

## Files

| File | Purpose |
|------|---------|
| `herbert.py` | CLI entrypoint |
| `adapter.py` | Queries Peacock DB and returns structured prescriptions |
| `mapper.py` | Maps Peacock `ui_invariant` strings to component specs |
| `HerbertAdapter.jsx` | React component that auto-renders the right UI for an API endpoint |
