import json
import os
from typing import Dict, Optional, List

class SnippetVault:
    """
    Lean Snippet Manager for MultiClip V2.
    Stores fixed text items (emails, dividers) that don't change.
    """
    def __init__(self, filepath: str = "/home/flintx/multiclip/snippets.json"):
        self.filepath = filepath
        self.snippets: Dict[int, str] = {i: "" for i in range(20)}
        self.load()

    def set_snippet(self, index: int, content: str):
        if 0 <= index < 20:
            self.snippets[index] = content
            self.save()

    def get_snippet(self, index: int) -> Optional[str]:
        return self.snippets.get(index)

    def save(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump({str(k): v for k, v in self.snippets.items()}, f, indent=4)
        except:
            pass

    def load(self):
        if not os.path.exists(self.filepath):
            # Pre-load your specific tunnel config and pip notes
            self.snippets[0] = "flintx@email.com"
            self.snippets[1] = "tunnel # Runs _ezenv_tunnel_toggle"
            self.snippets[2] = "export http_proxy=socks5h://127.0.0.1:1081; export https_proxy=socks5h://127.0.0.1:1081; export all_proxy=socks5h://127.0.0.1:1081"
            self.snippets[3] = "For pip I use socks5 tun0 1081 via the 'tunnel' alias."
            self.save()
            return

        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                for k, v in data.items():
                    self.snippets[int(k)] = v
        except:
            pass
