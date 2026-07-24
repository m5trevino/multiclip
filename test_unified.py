#!/usr/bin/env python3
"""
Test unified MultiClip + Clipman integration.
History is now integrated directly into the GUI.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.clipman_parser import ClipmanParser, SessionTracker


def test_unified_system():
    """Test the unified clipboard system."""
    print("=" * 70)
    print("MultiClip + Clipman Unified System Test")
    print("=" * 70)
    
    parser = ClipmanParser()
    print(f"\n📋 Reading from: {parser.filepath}")
    
    # Load history
    entries = parser.parse(max_entries=100)
    print(f"📊 Total history entries: {len(entries)}")
    
    # Show recent
    print("\n🕐 Recent 10 entries:")
    print("-" * 70)
    for i, entry in enumerate(entries[:10]):
        preview = entry.preview[:60] + "..." if len(entry.preview) > 60 else entry.preview
        print(f"  [{i:2d}] {preview}")
    
    # Demonstrate deployment workflow
    print("\n🎯 Deployment Workflow Demo:")
    print("-" * 70)
    
    selected_indices = [2, 5, 8]  # Simulating user selection
    selected_entries = [entries[i] for i in selected_indices if i < len(entries)]
    
    print(f"Selected {len(selected_entries)} entries for deployment:")
    for i, entry in enumerate(selected_entries):
        print(f"  Slot {i+1}: {entry.preview[:50]}...")
    
    # Simulate session tracking
    print("\n🔄 Session Mode Demo:")
    print("-" * 70)
    
    tracker = SessionTracker(timeout_seconds=180)
    tracker.start_session()
    
    test_copies = [
        "import numpy as np",
        "import pandas as pd",
        "df = pd.read_csv('data.csv')",
        "print(df.head())"
    ]
    
    for content in test_copies:
        tracker.add_entry(content)
        print(f"  Copied: {content[:40]}")
    
    print(f"\nSession has {len(tracker.entries)} items")
    print("Press Ctrl+V 4 times to paste each item in sequence")
    
    # Simulate sequential paste
    tracker.reset_sequence()
    print("\nSimulating sequential paste:")
    for i in range(4):
        entry = tracker.get_next()
        if entry:
            print(f"  [{i+1}] Pasted: {entry.content}")
    
    print("\n" + "=" * 70)
    print("✅ Unified system test complete!")
    print("=" * 70)
    print("""
🚀 NEW WORKFLOW:

1. MultiClip GUI opens with clipman history visible on the right
2. Scroll through your copy history (50+ items per page)
3. Click to select items you want (or use checkbox)
4. Click "Deploy to Slots" - loads into slots 1-10
5. Use Ctrl+Shift+1-9 to paste from slots
6. Or use Win+V for sequential paste
7. Or use Win+Alt+1 for bulk paste

📋 HOTKEYS:
   Ctrl+1-9        → Copy to slot
   Ctrl+Shift+1-9  → Paste from slot  
   Win+M           → Cycle modes
   Win+V           → Sequential paste (next item)
   Win+Alt+1       → Bulk paste all
   Win+Ctrl+1      → Bulk paste reverse
   Win+H           → Refresh history
   Win+S/E         → Start/End session
""")


if __name__ == "__main__":
    test_unified_system()
