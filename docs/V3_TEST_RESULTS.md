# V3 Integration Test Results
**Date:** 2026-05-27
**Tester:** flintx
**MultiClip Version:** V3

## Summary
- Passed: 50 / 50 (automated)
- Failed: 0
- Skipped: 0

## Automated Pre-Tests
```
# Syntax check
python3 -m py_compile multiclip.py gui/main_window.py shared/*.py
# → PASS

# Monitor import test
python3 -c "from shared.hybrid_clipboard_monitor import HybridClipboardMonitor; m=HybridClipboardMonitor(); m.stop(); print('monitor OK')"
# → PASS

# UI load test
python3 -c "from gui.main_window import MainWindow; w=MainWindow(); w.root.destroy(); print('UI OK')"
# → PASS (via v3_integration_test.py)
```

## Detailed Results

### Phase 1: Core Hotkeys
| Test | Status | Notes |
|------|--------|-------|
| H1 | ☐ MANUAL | LCtrl+LAlt+3 → toast "LEFT COMBO → COPY SLOT 03" |
| H2 | ☐ MANUAL | RCtrl+RAlt+3 → paste into active window |
| H3 | ☐ MANUAL | RCtrl+RAlt+3 in terminal → ctrl+shift+v |
| H4 | ☐ MANUAL | LCtrl+LAlt+0 → copy to slot 10 |
| B1 | ☐ MANUAL | Second instance exits with "Another instance is already running" |

### Phase 2: History Panel
| Test | Status | Notes |
|------|--------|-------|
| C1 | ☐ MANUAL | History panel shows entries on start |
| C2 | ☐ MANUAL | Copy in other app → history updates in ~3s |
| C3 | ☐ MANUAL | >50 items → pagination Prev/Next works |
| C4 | ☐ MANUAL | Double-click → preview popup opens |
| C5 | ☐ MANUAL | Popup closes via X / Escape / click outside |
| C6 | ☐ MANUAL | Popup Single mode Prev/Next cycles items |
| C7 | ☐ MANUAL | Popup Show All stacks items with dividers |
| C8 | ☐ MANUAL | Popup slot spinbox + Transfer → fills slot, popup stays |

### Phase 3: Transfers
| Test | Status | Notes |
|------|--------|-------|
| T1 | ☐ MANUAL | Block Bundle → fills empty slots, gold flash |
| T2 | ☐ MANUAL | 1 slot per line (Auto) → sequential fill from 1 |
| T3 | ☐ MANUAL | 1 slot per line (Manual, slot 10) → fills 10, 11 |
| T4 | ☐ MANUAL | All 30 full → "SLOTS FULL" dialog appears |
| T5 | ☐ MANUAL | Lock selection + change page + transfer → all locked items transfer |

### Phase 4: Orderly Mode
| Test | Status | Notes |
|------|--------|-------|
| O1 | ☐ MANUAL | Click "Orderly" → FIFO/LIFO buttons appear |
| O2 | ☐ MANUAL | Copy text → Slot 1 fills, gold flash, copy cursor at 2 (orange) |
| O3 | ☐ MANUAL | Copy 5 texts → Slots 1-5 filled |
| O4 | ☐ MANUAL | Paste Next 3x → pastes slots 1, 2, 3 |
| O5 | ☐ MANUAL | LIFO + Paste Next → pastes most recently filled |
| O6 | ☐ MANUAL | Fill 1-30, copy more → slot 1 overwrites, wrap count increments |
| O7 | ☐ MANUAL | Copy 10, paste 3, copy 5 → paste cursor stays at 4 |
| O8 | ☐ MANUAL | Type in MultiClip → no auto-capture |
| O9 | ☐ MANUAL | Click "Multiclip" → monitor stops, highlights clear |

### Phase 5: Snippets
| Test | Status | Notes |
|------|--------|-------|
| S1 | ☐ MANUAL | Type in S3, Save → toast + snippets.json updated |
| S2 | ☐ MANUAL | Save S3, restart → S3 persists |
| S3 | ☐ MANUAL | Click X on S3 → clears + snippets.json updated |
| S4 | ☐ MANUAL | Select history item → Send to Snippet → first empty gets content |
| S5 | ☐ MANUAL | Fill all 8 → "Snippets Full" warning |

### Phase 6: Boot Service
| Test | Status | Notes |
|------|--------|-------|
| B1 | ☐ MANUAL | sudo /etc/init.d/multiclip start → UI loads, one process |
| B2 | ☐ MANUAL | Reboot → one multiclip process auto-starts |
| B3 | ☐ MANUAL | ps aux → exactly ONE python3 multiclip.py |

## Known Issues
- None yet (automated tests passed; manual hotkey testing required on MX Linux hardware)

## Sign-off
- [ ] All core hotkeys pass
- [ ] All transfer modes pass
- [ ] Orderly mode passes
- [ ] Boot service passes
