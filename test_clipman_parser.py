#!/usr/bin/env python3
"""
Diagnostic script to test the Clipman parser on your live textsrc.

This version uses the exact path you provided:
    /home/flintx/.cache/xfce4/clipman/textsrc
"""

import os
import sys

# Add project root to path so we can import the parser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.clipman_parser import ClipmanParser


def main():
    # Use the exact path you gave
    textsrc_path = "/home/flintx/.cache/xfce4/clipman/textsrc"

    print("=" * 70)
    print("CLIPMAN PARSER DIAGNOSTIC")
    print(f"Using explicit path: {textsrc_path}")
    print("=" * 70)

    if not os.path.exists(textsrc_path):
        print(f"\nERROR: File not found at this path!")
        print(f"Checked: {textsrc_path}")
        print("Double-check the path or permissions (especially if running as root).")
        return

    try:
        size = os.path.getsize(textsrc_path)
        print(f"File size: {size / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"Could not get file size: {e}")

    # Initialize parser with the correct path
    parser = ClipmanParser(filepath=textsrc_path)

    print("\n--- NEW PARSER (Improved) ---")
    entries = parser.get_recent(100)

    print(f"Clean entries extracted (last 100): {len(entries)}")

    if entries:
        print("\nFirst 5 entries (most recent first):")
        for i, e in enumerate(entries[:5]):
            print(f"  [{i}] preview: {e.preview[:80]}")
            print(f"      words: {e.word_count}")
            print()

        total_words = sum(e.word_count for e in entries)
        print(f"Total words across 100 entries: {total_words}")
    else:
        print("No entries extracted. Parser still needs work on your format.")

    print("\n" + "=" * 70)
    print("If the previews above look clean and useful, we're in good shape.")
    print("Run this whenever you want to re-test after changes.")
    print("=" * 70)


if __name__ == "__main__":
    main()
