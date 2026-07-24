# DEVRYTHING_GOSPEL.md: MULTICLIP V2 INDUSTRIAL WORKSTATION

## I. GOSPEL SUMMARY
THE MULTICLIP V2 INDUSTRIAL WORKSTATION IS A DETERMINISTIC PIPELINE DESIGNED FOR HIGH-DENSITY CLIPBOARD MANAGEMENT AND TERMINAL-AWARE DATA INJECTION. IT ELIMINATES KEYBOARD CONFLICTS, PROVIDES INDUSTRIAL-GRADE FEEDBACK, AND PERSISTS DATA THROUGH A LEAN, INDUSTRIAL-GRADE VAULT.

## II. SYSTEM ARCHITECTURE (C4 CONTAINER MODEL)

```mermaid
graph TD
    subgraph S["SYSTEM: MULTICLIP V2"]
        ORCH[multiclip.py: ORCHESTRATOR]
        UI[gui/main_window.py: WORKSTATION]
        MANAGER[shared/clipboard_manager.py: 30-SLOT BENCH]
        PARSER[shared/clipman_parser.py: INDUSTRIAL PARSER]
        VAULT[shared/snippets_manager.py: SNIPPET VAULT]
    end

    CLIPMAN[(~/.cache/xfce4/clipman/textsrc)] -->|; DELIMITED DATA| PARSER
    PARSER -->|DECODED ENTRIES| MANAGER
    ORCH <--> UI
    ORCH <--> MANAGER
    ORCH <--> VAULT
    ORCH -->|CONTROL| PYAUTO[pyautogui/xdotool: INJECTION]
    PYAUTO -->|PASTE| APPS[TARGET APPLICATION]
```

## III. THE PASTE STRIKE PIPELINE (Win + V)

```mermaid
sequenceDiagram
    autonumber
    participant K as Keyboard
    participant O as Orchestrator
    participant M as Manager
    participant D as Detector (xdotool)
    participant I as Injector (pyautogui)

    K->>O: Win + V
    O->>M: Get Ordered IDs
    M-->>O: Slot Index
    O->>M: Fetch Content
    M-->>O: Content
    O->>D: is_terminal_active()
    D-->>O: Result (Term/Browser)
    O->>I: Copy to System Clipboard
    alt Is Terminal
        I->>I: Ctrl+Shift+V
    else Standard
        I->>I: Ctrl+V
    end
    O->>O: Toast Feedback
```

## IV. TECHNICAL INVARIANTS (THE LAW)
1.  **INDUSTRIAL PARSER**: Must parse `;` separated strings, handle `\;` (literal semicolon), `
` (newline), `\s` (space), `	` (tab). Reading from the end of the 31MB file is MANDATORY.
2.  **TERMINAL TAX**: Every paste operation must use `xdotool` to detect if the target is a terminal to correctly toggle `Ctrl+V` vs `Ctrl+Shift+V`.
3.  **UNIFIED BENCH**: The 30-slot grid holds all state. 1-30 numbering is handled by custom fields in the UI. Normalize sequence resets to 1-30.
4.  **OPERATIONAL TOAST**: Every command (Copy, Paste, Save, Edit) must return an industrial toast notification with: [Source/Slot] → [Action] → [Preview]. NO EXCEPTIONS.
5.  **VAULT INTEGRATION**: Snippets have persistent hotkeys (`Win + Alt + 1-0`).

## V. OPERATIONAL EMERGENCY: THE "STICKY SUPER"
If the Super key gets stuck, execute `pyautogui.keyUp('win')` immediately. The workstation has been calibrated to release it before every operation. 

**AUTHENTICATED BY DEVRYTHING_COLLECTIVE_01** 
**4SHO.**
