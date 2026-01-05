import os

class ClipImporter:
    @staticmethod
    def smart_parse(text: str) -> list:
        """
        Scans text. The first char that is NOT alphanumeric AND NOT a period (.)
        becomes the delimiter.
        """
        if not text: return []
        
        delimiter = None
        
        # 1. Find the delimiter
        for char in text:
            if not char.isalnum() and char != '.':
                delimiter = char
                break
        
        items = []
        if delimiter:
            # Split by found delimiter
            print(f"[Smart Parser] Detected delimiter: '{delimiter}'")
            items = [item.strip() for item in text.split(delimiter) if item.strip()]
        else:
            # Fallback: Split by newlines if no weird chars found
            items = [line.strip() for line in text.splitlines() if line.strip()]
            
        return items[:10] # Return max 10

    @staticmethod
    def parse_file(filepath: str) -> list:
        if not os.path.exists(filepath): return []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # Default file import uses newlines
            return [line.strip() for line in content.splitlines() if line.strip()][:10]
        except Exception as e:
            print(f"[Import Error] {e}")
            return []
