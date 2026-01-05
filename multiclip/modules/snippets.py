import json
from pathlib import Path

class SnippetManager:
    def __init__(self, filename="snippets.json"):
        self.file = Path(__file__).parent.parent.parent / filename
        self.snippets = self._load()

    def _load(self):
        if self.file.exists():
            try:
                with open(self.file, 'r') as f:
                    return json.load(f)
            except: pass
        # Default seed data
        return {"Name": "Matthew Trevino", "Email": "mtrevino1983@gmail.com"}

    def save(self):
        with open(self.file, 'w') as f:
            json.dump(self.snippets, f, indent=2)

    def add(self, key, value):
        self.snippets[key] = value
        self.save()

    def delete(self, key):
        if key in self.snippets:
            del self.snippets[key]
            self.save()
