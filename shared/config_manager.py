import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    def __init__(self, config_dir: str = "~/.multiclip"):
        self.config_dir = Path(config_dir).expanduser()
        self.config_file = self.config_dir / "config.json"
        self.state_file = self.config_dir / "state.json"
        self.snippets_file = self.config_dir / "snippets.json"
        
        self._ensure_config_dir()
        self.config = self._load_config()
    
    def _ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        default_config = {
            "hotkeys": {
                "copy_to_slot": "ctrl+{slot}",
                "paste_from_slot": "ctrl+shift+{slot}",
                "transfer_to_clipboard": "ctrl+alt+{slot}",
                "orderly_mode_toggle": "ctrl+shift+o",
                "orderly_copy": "ctrl+c",
                "orderly_paste": "ctrl+v",
                "snippers_view": "ctrl+shift+s",
                "main_gui": "ctrl+shift+m"
            },
            "gui": {
                "window_size": [800, 600],
                "always_on_top": False,
                "start_minimized": False,
                "show_slot_previews": True,
                "theme": "default"
            },
            "behavior": {
                "auto_save_state": True,
                "max_clipboard_history": 100,
                "paste_delay_ms": 50,
                "monitor_clipboard": True
            },
            "terminal": {
                "paste_command": "ctrl+shift+v",
                "detect_terminals": ["gnome-terminal", "xterm", "konsole", "terminal"],
                "format_commands": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to handle new config options
                return {**default_config, **loaded_config}
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        config_to_save = config or self.config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        keys = key_path.split('.')
        config_ref = self.config
        
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        config_ref[keys[-1]] = value
        self.save_config()
    
    def get_hotkey(self, action: str, slot: Optional[int] = None) -> Optional[str]:
        hotkey_template = self.get(f"hotkeys.{action}")
        if hotkey_template and slot is not None:
            return hotkey_template.format(slot=slot)
        return hotkey_template
    
    def save_state(self, state_data: Dict[str, Any]):
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading state: {e}")
        return {}
    
    def save_snippets(self, snippets_data: Dict[str, Any]):
        try:
            with open(self.snippets_file, 'w') as f:
                json.dump(snippets_data, f, indent=2)
        except Exception as e:
            print(f"Error saving snippets: {e}")
    
    def load_snippets(self) -> Dict[str, Any]:
        if self.snippets_file.exists():
            try:
                with open(self.snippets_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading snippets: {e}")
        return {"categories": {}, "commands": {}}
