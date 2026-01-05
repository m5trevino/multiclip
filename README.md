# 📋 MULTICLIP v2.2
**The Arsenal / Sequential Data Ingest**

## 💀 THE MISSION
A tactical clipboard manager designed for high-velocity data entry. It allows the operator to "load" multiple slots (1-10) with data and paste them in a specific sequence, or access them randomly via global hotkeys.

## 🏗️ ARCHITECTURE
*   **Framework:** Python (Tkinter) + `keyboard` + `pyperclip`.
*   **Overlay:** Always-on-top "HUD" for situational awareness.
*   **Input:** Smart Parser detects delimiters to split bulk text into slots automatically.

## 🚀 PROTOCOLS
### 1. Launch System
`python3 multiclip.py`

## 🛠️ FEATURES
*   **Sequential Mode:** Copy A, B, C -> Paste A, B, C (One key press).
*   **Smart Ingest:** Paste a CSV or delimited string, and it auto-populates slots.
*   **The HUD:** visual confirmation of the "Chambered" clip.
