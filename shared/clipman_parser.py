"""
Improved Clipman History Parser
Tuned for real-world XFCE Clipman textsrc files with heavy terminal noise.
"""

import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ClipEntry:
    """Clean clipboard entry from Clipman history."""
    id: int
    content: str
    preview: str = ""
    word_count: int = 0

    def __post_init__(self):
        self.decoded_content = self._decode(self.content)
        if not self.preview:
            self.preview = self._make_preview()
        self.word_count = len(self.decoded_content.split())

    @staticmethod
    def _decode(text: str) -> str:
        """Decode Clipman escape sequences."""
        text = text.replace('\\;', ';')
        text = text.replace('\\n', '\n')
        text = text.replace('\\s', ' ')
        text = text.replace('\\t', '\t')
        text = text.replace('\\r', '')
        return text

    def _make_preview(self, max_len: int = 80) -> str:
        """Generate a clean single-line preview."""
        lines = self.decoded_content.split('\n')
        first_line = ""
        for line in lines:
            stripped = line.strip()
            if stripped:
                first_line = stripped
                break
        if len(first_line) > max_len:
            return first_line[:max_len - 3] + "..."
        return first_line or "(empty)"

    @property
    def is_empty(self) -> bool:
        return not self.decoded_content.strip()


class ClipmanParser:
    """
    Robust parser for ~/.cache/xfce4/clipman/textsrc
    """

    def __init__(self, filepath: Optional[str] = None):
        if filepath is None:
            default = os.path.expanduser("~/.cache/xfce4/clipman/textsrc")

            if os.path.exists(default):
                filepath = default
            else:
                # Running as root (or different user) — Clipman textsrc lives in the desktop user's home.
                # Common when doing "sudo su" or launching the hotkey app as root.
                sudo_user = os.environ.get("SUDO_USER")
                candidates = []

                if sudo_user and sudo_user != "root":
                    candidates.append(f"/home/{sudo_user}/.cache/xfce4/clipman/textsrc")

                # Hard fallback for this environment (flintx on MX Linux)
                candidates.append("/home/flintx/.cache/xfce4/clipman/textsrc")

                for cand in candidates:
                    if os.path.exists(cand):
                        filepath = cand
                        break
                else:
                    # Last resort — still use default (will be empty)
                    filepath = default

            # Diagnostic so user knows what's happening when run as root
            print(f"[ClipmanParser] Using textsrc: {filepath}  (exists={os.path.exists(filepath)})")

        self.filepath = filepath

    def parse(self, max_entries: int = 200) -> List[ClipEntry]:
        """Return most recent entries first (newest = index 0)."""
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                data = f.read()

            # Strip header if present
            if data.startswith('[texts]\ntexts='):
                data = data[len('[texts]\ntexts='):]

            # Split on unescaped semicolons
            entries_raw = self._split_on_unescaped_semicolon(data)

            # Most recent entries are at the end of the file
            recent_raw = [r for r in reversed(entries_raw) if r.strip()]

            entries: List[ClipEntry] = []
            for idx, raw in enumerate(recent_raw):
                if len(entries) >= max_entries:
                    break
                entry = ClipEntry(id=idx, content=raw)
                if not entry.is_empty:
                    entries.append(entry)

            return entries

        except Exception as e:
            print(f"[ClipmanParser] Error: {e}")
            return []

    def _split_on_unescaped_semicolon(self, text: str) -> List[str]:
        """Split string on ';' but respect escaped '\;'."""
        parts = []
        current = []
        i = 0
        length = len(text)

        while i < length:
            if text[i] == '\\' and i + 1 < length and text[i + 1] == ';':
                current.append('\\;')
                i += 2
            elif text[i] == ';':
                parts.append(''.join(current))
                current = []
                i += 1
            else:
                current.append(text[i])
                i += 1

        if current:
            parts.append(''.join(current))

        return parts

    def get_recent(self, count: int = 50) -> List[ClipEntry]:
        return self.parse(max_entries=count)


# Quick standalone test helper
if __name__ == "__main__":
    parser = ClipmanParser()
    entries = parser.get_recent(20)
    print(f"Found {len(entries)} recent entries\n")
    for i, e in enumerate(entries[:5]):
        print(f"[{i}] {e.preview}")
        print("-" * 60)
