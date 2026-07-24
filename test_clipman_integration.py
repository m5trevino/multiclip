#!/usr/bin/env python3
"""
Test script for MultiClip + Clipman integration.
Demonstrates the parser and session tracker.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.clipman_parser import ClipmanParser, SessionTracker


def test_parser():
    """Test the clipman parser."""
    print("=" * 60)
    print("Testing Clipman Parser")
    print("=" * 60)
    
    parser = ClipmanParser()
    print(f"\nReading from: {parser.filepath}")
    
    # Get recent entries
    entries = parser.get_recent(count=10)
    print(f"\nFound {len(entries)} recent entries:\n")
    
    for i, entry in enumerate(entries):
        print(f"[{i}] {entry.preview[:60]}...")
        print(f"    Words: {entry.word_count}, Chars: {len(entry.content)}")
        print()
    
    # Test search
    print("\n" + "=" * 60)
    print("Testing Search (query: 'python')")
    print("=" * 60)
    
    results = parser.search("python", max_results=5)
    print(f"\nFound {len(results)} matches:\n")
    
    for entry in results:
        print(f"- {entry.preview[:70]}")


def test_session_tracker():
    """Test the session tracker."""
    print("\n" + "=" * 60)
    print("Testing Session Tracker")
    print("=" * 60)
    
    tracker = SessionTracker(timeout_seconds=60)
    
    # Start session
    tracker.start_session()
    print("\nSession started!")
    
    # Simulate copying items
    test_contents = [
        "First item copied",
        "Second item with more text here",
        "Third item - code snippet: print('hello')",
        "Fourth item - email address",
        "Fifth item - final copy"
    ]
    
    for content in test_contents:
        tracker.add_entry(content)
        print(f"Added: {content[:40]}...")
    
    print(f"\nTotal in session: {len(tracker.entries)}")
    print(f"Progress: {tracker.get_progress()}")
    
    # Simulate sequential paste
    print("\nSimulating sequential paste (forward):")
    tracker.reset_sequence()
    for _ in range(3):
        entry = tracker.get_next()
        if entry:
            print(f"  Pasted: {entry.preview[:40]}...")
            print(f"  Progress: {tracker.get_progress()}")
    
    # Test reverse
    print("\nSimulating sequential paste (reverse):")
    tracker.set_direction("reverse")
    for _ in range(3):
        entry = tracker.get_next()
        if entry:
            print(f"  Pasted: {entry.preview[:40]}...")


def test_bulk_paste():
    """Demonstrate bulk paste functionality."""
    print("\n" + "=" * 60)
    print("Testing Bulk Paste")
    print("=" * 60)
    
    parser = ClipmanParser()
    entries = parser.get_recent(count=5)
    
    print(f"\nBulk pasting {len(entries)} items:\n")
    
    combined = "\n\n---\n\n".join([e.content.replace('\\n', '\n') for e in entries])
    print(combined[:500] + "..." if len(combined) > 500 else combined)


if __name__ == "__main__":
    test_parser()
    test_session_tracker()
    test_bulk_paste()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nHotkey Summary:")
    print("  Ctrl+1-9        : Copy to slot")
    print("  Ctrl+Shift+1-9  : Paste from slot")
    print("  Win+M           : Cycle modes")
    print("  Win+H           : Open history browser")
    print("  Win+V           : Sequential paste")
    print("  Win+Alt+1       : Bulk paste forward")
    print("  Win+Ctrl+1      : Bulk paste reverse")
    print("  Win+S           : Start session")
    print("  Win+E           : End session")
