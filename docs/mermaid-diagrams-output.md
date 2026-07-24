# MultiClip V2 — Mermaid Diagrams

> Generated per the `mermaid-diagrams` skill instructions.
> Each diagram is focused on a single concept with clear labels, explicit directions, and grouped elements.

---

## 1. System Context (C4 Context)

High-level view of MultiClip V2 and its external interactions.

```mermaid
C4Context
    title System Context — MultiClip V2

    Person(user, "User", "Desktop user managing clipboard across applications")
    System(multiclip, "MultiClip V2", "Advanced clipboard manager with 30 slots, hotkeys, and history")
    System_Ext(xfce, "XFCE Clipman", "System clipboard history daemon (textsrc)")
    System_Ext(x11, "X11 / Xdotool", "Window system for paste injection and focus detection")
    System_Ext(notify, "notify-send", "Desktop notification service")

    Rel(user, multiclip, "Triggers hotkeys (Ctrl+Alt+digit)")
    Rel(multiclip, user, "Shows toast notifications")
    Rel(multiclip, xfce, "Reads clipboard history (~/.cache/xfce4/clipman/textsrc)")
    Rel(multiclip, x11, "Detects active window, injects paste via xdotool")
    Rel(multiclip, notify, "Sends action feedback notifications")
```

---

## 2. Container Diagram (C4 Container)

Internal containers and their responsibilities.

```mermaid
C4Container
    title Container Diagram — MultiClip V2

    Person(user, "User")

    System_Boundary(multiclip, "MultiClip V2") {
        Container(main, "multiclip.py", "Python + tkinter", "Main app: hotkeys, slots, persistence, UI orchestration")
        Container(cli, "clipman_cli.py", "Python + curses", "Terminal browser for clipman history")
        Container(gui, "gui/main_window.py", "Python + tkinter", "Dense 30-slot workbench UI with clipman panel")
        Container(history, "gui/history_panel.py", "Python + tkinter", "Scrollable history with search/deploy")
        Container(diff_ui, "diff_marker/diff_interface.py", "Python + tkinter", "Side-by-side text diff UI")

        Container(shared, "shared/ modules", "Python", "Clipboard, parser, config, snippets")
        Container(diff_core, "diff_marker/ core", "Python + difflib", "Diff engine and types")
    }

    ContainerDb(state, "clipboard_dict.json", "JSON", "30-slot state persistence")
    ContainerDb(snippets, "snippets.json", "JSON", "Persistent snippet vault")
    ContainerDb(config, "~/.multiclip/config.json", "JSON", "User configuration")
    System_Ext(clipman_src, "XFCE textsrc", "Flat file", "Clipman history source")

    Rel(user, main, "Hotkeys + GUI")
    Rel(user, cli, "Terminal browsing")

    Rel(main, gui, "Renders workbench UI")
    Rel(main, history, "Wires clipman panel")
    Rel(main, shared, "Uses")
    Rel(main, state, "Loads / Saves slots")
    Rel(main, snippets, "Loads snippets")

    Rel(cli, shared, "Uses parser")
    Rel(diff_ui, diff_core, "Calculates diffs")
    Rel(diff_ui, shared, "Loads slot content")

    Rel(shared, clipman_src, "Parses history")
    Rel(shared, config, "Reads / Writes")
```

---

## 3. Class Diagram — Core Domain

Object model for clipboard management and clipman parsing.

```mermaid
classDiagram
    direction LR

    class ClipboardSlot {
        +int id
        +str content
        +int order
        +datetime timestamp
        +str preview
        +update_content(str)
        +to_dict() dict
        -_generate_preview() str
    }

    class ClipboardManager {
        +Dict[int, ClipboardSlot] slots
        +int num_slots
        +store_in_slot(int, str) bool
        +get_slot_content(int) Optional~str~
        +get_ordered_indices() List~int~
        +clear_all_slots()
    }

    class ClipEntry {
        +int id
        +str content
        +str preview
        +int word_count
        +str decoded_content
        +bool is_empty
        -_decode(str) str
        -_make_preview(int) str
    }

    class ClipmanParser {
        +str filepath
        +parse(int) List~ClipEntry~
        +get_recent(int) List~ClipEntry~
        -_split_on_unescaped_semicolon(str) List~str~
    }

    class ConfigManager {
        +Path config_dir
        +Path config_file
        +Path state_file
        +Dict config
        +get(str) Any
        +set(str, Any)
        +get_hotkey(str, Optional~int~) Optional~str~
        +save_state(dict)
        +load_state() dict
        +save_snippets(dict)
        +load_snippets() dict
    }

    class SnippetVault {
        +str filepath
        +Dict[int, str] snippets
        +set_snippet(int, str)
        +get_snippet(int) Optional~str~
        +save()
        +load()
    }

    ClipboardManager "1" --> "*" ClipboardSlot : manages
    ClipmanParser ..> ClipEntry : creates
    ConfigManager ..> SnippetVault : configures
```

---

## 4. Class Diagram — Diff Marker Module

Diff comparison subsystem.

```mermaid
classDiagram
    direction LR

    class DiffType {
        <<enumeration>>
        EQUAL
        INSERT
        DELETE
        REPLACE
    }

    class DiffLine {
        +Optional~int~ line_num_left
        +Optional~int~ line_num_right
        +str content_left
        +str content_right
        +DiffType diff_type
    }

    class DiffResult {
        +List~DiffLine~ lines
        +dict stats
        +str unified_diff
        -_calculate_stats() dict
    }

    class DiffManager {
        +int max_text_size
        +calculate_diff(str, str, int) DiffResult
        +format_unified_diff(DiffResult) str
        +get_diff_stats(DiffResult) str
        -_generate_side_by_side_diff(List~str~, List~str~) List~DiffLine~
    }

    class DiffInterface {
        +clipboard_manager
        +DiffManager diff_manager
        +DiffResult current_diff_result
        +str view_mode
        +_create_ui()
        +_perform_diff()
        +_refresh_diff_display()
        +_save_result()
        +_update_status(str)
    }

    DiffResult "1" --> "*" DiffLine : contains
    DiffManager ..> DiffResult : produces
    DiffInterface --> DiffManager : uses
    DiffLine --> DiffType : typed by
```

---

## 5. Flowchart — Hotkey Processing Pipeline

How the system handles global hotkey input to perform copy or paste actions.

```mermaid
flowchart TD
    A([Key Press Event]) --> B{Modifier held?}
    B -->|Ctrl + Alt| C{Digit key?}
    B -->|Other key| D[Ignore]
    C -->|Yes| E{Right-side modifiers?}
    C -->|No| D
    E -->|Yes| F["Paste from Slot<br/>RCtrl+RAlt+digit"]
    E -->|No| G["Copy to Slot<br/>LCtrl+LAlt+digit"]
    F --> H[Read slot content]
    H --> I{Content empty?}
    I -->|Yes| J[Log: empty slot]
    I -->|No| K[Copy to system clipboard]
    K --> L{Active window is terminal?}
    L -->|Yes| M["xdotool ctrl+shift+v"]
    L -->|No| N["xdotool ctrl+v"]
    M --> O[Show toast notification]
    N --> O
    J --> P([End])
    O --> P
    G --> Q[Trigger Ctrl+C via pyautogui]
    Q --> R[Read system clipboard]
    R --> S{Content exists?}
    S -->|Yes| T[Store in slot N]
    T --> U[Save to clipboard_dict.json]
    U --> V[Show toast: COPIED]
    S -->|No| W[Log: nothing captured]
    V --> P
    W --> P
    D --> P
```

---

## 6. Sequence Diagram — Copy Operation

Interaction sequence when user copies selected text into a slot.

```mermaid
sequenceDiagram
    actor User
    participant Main as multiclip.py
    participant KB as pynput Listener
    participant PA as pyautogui
    participant PC as pyperclip
    participant Slots as ClipboardManager
    participant FS as clipboard_dict.json
    participant Notify as notify-send

    User->>KB: Press LCtrl+LAlt+3
    KB->>Main: on_press(key='3')<br/>held_mods = {ctrl_l, alt_l}
    Main->>Main: _handle_combo(slot=3)
    Main->>PA: keyUp(all modifiers)
    Main->>PA: hotkey('ctrl', 'c')
    PA-->>User: System copies selection
    Main->>PC: paste()
    PC-->>Main: clipboard content
    alt Content exists
        Main->>Slots: slots['3'] = content
        Slots-->>Main: updated
        Main->>FS: json.dump(slots)
        FS-->>Main: persisted
        Main->>Notify: notify-send(title, preview)
        Notify-->>User: Toast: LEFT COMBO → COPY SLOT 03
    else Content empty
        Main->>Main: print("Nothing captured")
    end
```

---

## 7. Sequence Diagram — Paste Operation

Interaction sequence when user pastes from a slot into the active window.

```mermaid
sequenceDiagram
    actor User
    participant Main as multiclip.py
    participant KB as pynput Listener
    participant PC as pyperclip
    participant X11 as xdotool
    participant Notify as notify-send

    User->>KB: Press RCtrl+RAlt+3
    KB->>Main: on_press(key='3')<br/>held_mods = {ctrl_r, alt_r}
    Main->>Main: _handle_combo(slot=3)
    Main->>Main: paste_from_slot(3)
    Main->>Main: _release_all_modifiers()
    Main->>PC: copy(slot_content)
    Main->>X11: getactivewindow
    X11-->>Main: window ID
    Main->>X11: xprop WM_CLASS
    X11-->>Main: window class
    alt Terminal detected
        Main->>X11: key --clearmodifiers ctrl+shift+v
    else Regular window
        Main->>X11: key --clearmodifiers ctrl+v
    end
    X11-->>User: Paste injected into target
    Main->>Notify: notify-send(title, preview)
    Notify-->>User: Toast: RIGHT COMBO → PASTE SLOT 03
```

---

## 8. State Diagram — Application Lifecycle

States of the MultiClip V2 application from startup to shutdown.

```mermaid
stateDiagram-v2
    [*] --> Initializing
    Initializing --> SingleInstanceCheck : start
    SingleInstanceCheck --> LoadingState : flock acquired
    SingleInstanceCheck --> [*] : already running
    LoadingState --> RegisteringHotkeys : load clipboard_dict.json
    RegisteringHotkeys --> RunningGUI : pynput listener started
    RunningGUI --> HandlingCopy : LCtrl+LAlt+digit
    RunningGUI --> HandlingPaste : RCtrl+RAlt+digit
    HandlingCopy --> RunningGUI : complete
    HandlingPaste --> RunningGUI : complete
    RunningGUI --> LivePolling : start_live_clipman_refresh()
    LivePolling --> RunningGUI : stop poll
    RunningGUI --> EditingSlot : right-click slot
    EditingSlot --> RunningGUI : save / cancel
    RunningGUI --> TransferringClipman : transfer selected entries
    TransferringClipman --> RunningGUI : slots updated
    RunningGUI --> ShuttingDown : SIGINT / SIGTERM / close window
    ShuttingDown --> [*] : emergency_save() + exit
```

---

## 9. ER Diagram — Data Model

Relationships between persisted entities in the MultiClip system.

```mermaid
erDiagram
    SLOTS ||--o{ SNIPPETS : references
    SLOTS ||--o{ CLIPMAN_HISTORY : transfers_to
    CONFIG ||--o{ SLOTS : configures_behavior
    CONFIG ||--o{ SNIPPETS : configures_hotkeys

    SLOTS {
        int slot_id PK
        string content
        int order
        string preview
        datetime timestamp
    }

    SNIPPETS {
        int snippet_id PK
        string content
        string label
    }

    CLIPMAN_HISTORY {
        int entry_id PK
        string raw_content
        string decoded_content
        string preview
        int word_count
    }

    CONFIG {
        string key PK
        json value
        string section
    }

    DIFF_RESULT {
        int diff_id PK
        string unified_diff
        int additions
        int deletions
        int modifications
        int total_lines
    }
```

---

## 10. Mindmap — Project Feature Hierarchy

Hierarchical breakdown of MultiClip V2 capabilities.

```mermaid
mindmap
  root((MultiClip V2))
    Clipboard Core
      30 Persistent Slots
      Hotkey Copy / Paste
      System Clipboard Bridge
      Toast Notifications
    GUI Interface
      Workbench 30-Slot Grid
      Clipman History Panel
      Snippet Vault
      Edit Overlay Modal
      Preview Popup
    CLI Tools
      Curses History Browser
      Multi-Select Deployment
      Ordered Selection Mode
    Data Layer
      Clipman Parser
      Config Manager
      Snippet Vault
      Diff Marker
    System Integration
      X11 / xdotool Paste
      Terminal Detection
      notify-send Alerts
      Single Instance Lock
```

---

## 11. Flowchart — Clipman History Transfer Flow

How selected clipman history entries flow into OG slots.

```mermaid
flowchart LR
    A([User selects<br/>clipman entries]) --> B{Transfer mode?}
    B -->|Batch| C["Each item →<br/>separate slot"]
    B -->|One Slot| D["Join all items<br/>with \\n\\n"]
    C --> E["Find empty slots<br/>1-30"]
    D --> F["Pick target slot<br/>(or oldest)"]
    E --> G{Slots available?}
    G -->|Yes| H[Assign to next empty]
    G -->|No| I[Prompt user for<br/>target slot 1-30]
    H --> J[Save slots to<br/>clipboard_dict.json]
    I --> J
    F --> J
    J --> K[Refresh UI slot displays]
    K --> L[Show toast:<br/>CLIPMAN → TRANSFER]
    L --> M([Done])
```

---

## 12. GitGraph — Development Branch History

Conceptual branch structure for the MultiClip V2 evolution.

```mermaid
gitgraph
    commit id: "initial-v1"
    commit id: "add-30-slots"
    branch feature/diff-marker
    commit id: "diff-engine"
    commit id: "diff-ui"
    checkout main
    merge feature/diff-marker tag: "v1.5"
    commit id: "add-clipman-parser"
    branch feature/clipman-integration
    commit id: "parser-module"
    commit id: "history-panel"
    commit id: "live-polling"
    checkout main
    merge feature/clipman-integration tag: "v2.0"
    commit id: "dense-gui-layout"
    branch hotfix/root-paste
    commit id: "xdotool-fallback"
    checkout main
    merge hotfix/root-paste tag: "v2.1"
    commit id: "snippet-vault"
    commit id: "config-manager"
```

---

## Legend

| Symbol / Pattern | Meaning |
| ---------------- | ------- |
| `C4Context` | Level 1 architecture — users and external systems |
| `C4Container` | Level 2 architecture — internal applications and data stores |
| `classDiagram` | OOP structure with inheritance, composition, and associations |
| `flowchart TD/LR` | Process flow with decisions and actions |
| `sequenceDiagram` | Time-ordered interaction between actors and components |
| `stateDiagram-v2` | Application state machine with transitions |
| `erDiagram` | Entity relationships and cardinality |
| `mindmap` | Hierarchical feature or concept breakdown |
| `gitgraph` | Branch and merge history |

---

*End of diagrams. Each visualization above is focused on a single concern per the mermaid-diagrams skill best practices.*
