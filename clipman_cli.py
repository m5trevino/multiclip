#!/usr/bin/env python3
"""
Clipman History Browser - Curses-based CLI
Browse clipman history, select multiple entries, and deploy to slots.
"""

import curses
import curses.ascii
import os
import sys
import json
from typing import List, Set, Optional, Callable
from dataclasses import dataclass, asdict

# Add shared to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shared.clipman_parser import ClipmanParser, ClipEntry


@dataclass
class Selection:
    """Represents a selected entry with optional ordering."""
    entry: ClipEntry
    order: Optional[int] = None  # For ordered deployment mode


class ClipmanBrowser:
    """
    Curses-based browser for clipman history.
    
    Features:
    - Browse history with up/down arrows
    - Multi-select with Space
    - Number keys 1-9 for ordered selection
    - Left/Right arrows for paging
    - Enter to deploy selected to slots
    """
    
    def __init__(self, deploy_callback: Callable = None):
        self.parser = ClipmanParser()
        self.entries: List[ClipEntry] = []
        self.selected: Set[int] = set()  # Indices of selected entries
        self.ordered_selections: dict = {}  # idx -> order number
        self.current_idx = 0
        self.page = 0
        self.page_size = 50
        self.mode = "normal"  # "normal", "ordered"
        self.status_message = ""
        self.deploy_callback = deploy_callback
        
    def load_entries(self, max_entries: int = 500):
        """Load entries from clipman history."""
        self.entries = self.parser.parse(max_entries=max_entries)
        
    def init_colors(self):
        """Initialize color pairs."""
        curses.start_color()
        curses.use_default_colors()
        
        # Color pairs
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)      # Normal
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)      # Highlighted
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)      # Selected
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)     # Ordered
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)       # Header
        curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)        # Status/warning
        
    def draw_header(self, stdscr, width: int):
        """Draw the header bar."""
        header_text = f" Clipman History Browser | {len(self.entries)} entries | {len(self.selected)} selected "
        mode_text = f" [Mode: {self.mode.upper()}] "
        
        # Center the header
        x = max(0, (width - len(header_text)) // 2)
        stdscr.addstr(0, 0, " " * width, curses.color_pair(5) | curses.A_REVERSE)
        stdscr.addstr(0, x, header_text, curses.color_pair(5) | curses.A_REVERSE)
        
        # Mode indicator on the right
        stdscr.addstr(0, width - len(mode_text) - 1, mode_text, curses.color_pair(5) | curses.A_BOLD)
        
    def draw_footer(self, stdscr, height: int, width: int):
        """Draw the footer with help text."""
        if self.mode == "ordered":
            help_text = " 1-9:Order | Enter:Deploy | Q:Quit | Arrows:Navigate | Space:Toggle "
        else:
            help_text = " Space:Select | Enter:Deploy | Q:Quit | Arrows:Navigate | O:Ordered Mode "
        
        footer = help_text[:width-1]
        stdscr.addstr(height - 2, 0, footer, curses.color_pair(5))
        stdscr.addstr(height - 2, len(footer), " " * (width - len(footer) - 1), curses.color_pair(5))
        
        # Status message
        if self.status_message:
            msg = self.status_message[:width-1]
            stdscr.addstr(height - 1, 0, msg, curses.color_pair(6))
            
    def draw_list(self, stdscr, start_y: int, height: int, width: int):
        """Draw the scrollable list of entries."""
        visible_height = height - start_y - 2  # Leave room for footer
        
        # Calculate page
        total_pages = (len(self.entries) + self.page_size - 1) // self.page_size
        start_idx = self.page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.entries))
        
        # Draw page indicator
        page_text = f" Page {self.page + 1}/{max(1, total_pages)} "
        stdscr.addstr(start_y, width - len(page_text), page_text, curses.color_pair(5))
        
        # Draw entries
        for i in range(start_idx, end_idx):
            row = start_y + 1 + (i - start_idx)
            if row >= height - 2:
                break
                
            entry = self.entries[i]
            is_selected = i in self.selected
            is_current = i == self.current_idx
            has_order = i in self.ordered_selections
            
            # Prepare display text
            idx_str = f"{i:4d} "
            order_str = f"[{self.ordered_selections[i]}] " if has_order else "    "
            
            # Truncate preview to fit
            max_preview = width - len(idx_str) - len(order_str) - 3
            preview = entry.preview[:max_preview]
            
            # Build line
            line = f"{idx_str}{order_str}{preview}"
            line = line[:width-1]
            
            # Choose color
            if is_current and is_selected:
                attr = curses.color_pair(3) | curses.A_REVERSE | curses.A_BOLD
            elif is_current:
                attr = curses.color_pair(2) | curses.A_BOLD
            elif is_selected and has_order:
                attr = curses.color_pair(4) | curses.A_BOLD
            elif is_selected:
                attr = curses.color_pair(3)
            else:
                attr = curses.color_pair(1)
                
            # Alternating row background
            if not is_current and (i - start_idx) % 2 == 1:
                attr |= curses.A_DIM
                
            stdscr.addstr(row, 0, line + " " * (width - len(line) - 1), attr)
            
    def draw_preview(self, stdscr, width: int, height: int):
        """Draw preview of current entry at bottom."""
        if not self.entries:
            return
            
        preview_y = height - 5
        entry = self.entries[self.current_idx]
        
        # Separator line
        stdscr.addstr(preview_y, 0, "─" * width, curses.color_pair(5))
        
        # Show first 3 lines of content
        lines = entry.get_display_text().split('\n')[:3]
        for i, line in enumerate(lines):
            if preview_y + 1 + i < height - 2:
                truncated = line[:width-4]
                stdscr.addstr(preview_y + 1 + i, 2, truncated, curses.color_pair(1))
                
    def deploy_selections(self, ordered: bool = False):
        """Deploy selected entries to slots."""
        if not self.selected:
            self.status_message = "No items selected!"
            return
            
        selections = []
        if ordered and self.ordered_selections:
            # Sort by order number
            ordered_items = sorted(self.ordered_selections.items(), key=lambda x: x[1])
            for idx, order in ordered_items:
                selections.append(self.entries[idx])
        else:
            # Use selection order (most recently selected first, so reverse)
            for idx in sorted(self.selected):
                selections.append(self.entries[idx])
                
        # Call deploy callback or save to file
        if self.deploy_callback:
            self.deploy_callback(selections, ordered)
        else:
            # Save to deploy queue file
            self._save_deploy_queue(selections)
            
        self.status_message = f"Deployed {len(selections)} items to slots!"
        
    def _save_deploy_queue(self, selections: List[ClipEntry]):
        """Save selections to a queue file for multiclip to read."""
        queue_file = os.path.expanduser("~/.cache/multiclip/deploy_queue.json")
        os.makedirs(os.path.dirname(queue_file), exist_ok=True)
        
        data = {
            "selections": [{"content": e.content, "preview": e.preview} for e in selections],
            "timestamp": str(datetime.now())
        }
        
        with open(queue_file, 'w') as f:
            json.dump(data, f)
            
    def toggle_selection(self):
        """Toggle selection of current entry."""
        if self.current_idx in self.selected:
            self.selected.discard(self.current_idx)
            if self.current_idx in self.ordered_selections:
                del self.ordered_selections[self.current_idx]
        else:
            self.selected.add(self.current_idx)
            
    def set_order(self, order_num: int):
        """Set order number for current selection."""
        if self.current_idx not in self.selected:
            self.selected.add(self.current_idx)
        self.ordered_selections[self.current_idx] = order_num
        
    def run(self, stdscr):
        """Main curses loop."""
        # Setup
        curses.curs_set(0)  # Hide cursor
        stdscr.clear()
        self.init_colors()
        
        # Load entries
        self.load_entries()
        self.status_message = f"Loaded {len(self.entries)} entries"
        
        while True:
            height, width = stdscr.getmaxyx()
            stdscr.clear()
            
            # Draw UI
            self.draw_header(stdscr, width)
            self.draw_list(stdscr, 1, height, width)
            self.draw_preview(stdscr, width, height)
            self.draw_footer(stdscr, height, width)
            
            stdscr.refresh()
            
            # Handle input
            try:
                key = stdscr.getch()
            except:
                break
                
            if key == ord('q') or key == ord('Q'):
                break
                
            elif key == curses.KEY_UP:
                if self.current_idx > 0:
                    self.current_idx -= 1
                    if self.current_idx < self.page * self.page_size:
                        self.page -= 1
                        
            elif key == curses.KEY_DOWN:
                if self.current_idx < len(self.entries) - 1:
                    self.current_idx += 1
                    if self.current_idx >= (self.page + 1) * self.page_size:
                        self.page += 1
                        
            elif key == curses.KEY_LEFT:
                if self.page > 0:
                    self.page -= 1
                    self.current_idx = self.page * self.page_size
                    
            elif key == curses.KEY_RIGHT:
                total_pages = (len(self.entries) + self.page_size - 1) // self.page_size
                if self.page < total_pages - 1:
                    self.page += 1
                    self.current_idx = self.page * self.page_size
                    
            elif key == ord(' '):
                self.toggle_selection()
                
            elif key == ord('o') or key == ord('O'):
                if self.mode == "normal":
                    self.mode = "ordered"
                    self.status_message = "ORDERED MODE: Press 1-9 to assign order"
                else:
                    self.mode = "normal"
                    self.ordered_selections.clear()
                    self.status_message = "Normal mode"
                    
            elif key == ord('\n') or key == curses.KEY_ENTER:
                self.deploy_selections(ordered=(self.mode == "ordered"))
                
            elif ord('1') <= key <= ord('9'):
                if self.mode == "ordered":
                    self.set_order(key - ord('0'))
                else:
                    # In normal mode, number keys could jump to that slot
                    pass
                    
            # Clear status after a few seconds (simplified)
            if self.status_message and key != -1:
                pass  # Keep status until next action


def main():
    """Entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Browse clipman history")
    parser.add_argument("--max", type=int, default=500, help="Max entries to load")
    args = parser.parse_args()
    
    app = ClipmanBrowser()
    
    try:
        curses.wrapper(app.run)
    except KeyboardInterrupt:
        pass
    
    print("Clipman browser closed.")


if __name__ == "__main__":
    from datetime import datetime
    main()
