import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

class SnippetCommand:
    def __init__(self, content: str, description: str = "", variables: List[str] = None):
        self.id = str(uuid.uuid4())
        self.content = content
        self.description = description
        self.variables = variables or self._extract_variables(content)
        self.usage_count = 0
        self.created_at = datetime.now()
        self.last_used = None
    
    def _extract_variables(self, content: str) -> List[str]:
        # Extract 'var' placeholders from command
        pattern = r'\bvar\b'
        matches = re.findall(pattern, content)
        # Number them sequentially
        return [f"var{i+1}" for i in range(len(matches))]
    
    def use(self):
        self.usage_count += 1
        self.last_used = datetime.now()
    
    def substitute_variables(self, variable_values: Dict[str, str]) -> str:
        result = self.content
        for i, var_name in enumerate(self.variables):
            if var_name in variable_values:
                # Replace the i-th occurrence of 'var' with the actual value
                result = result.replace('var', variable_values[var_name], 1)
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "description": self.description,
            "variables": self.variables,
            "usage_count": self.usage_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        cmd = cls(data["content"], data.get("description", ""), data.get("variables", []))
        cmd.id = data.get("id", str(uuid.uuid4()))
        cmd.usage_count = data.get("usage_count", 0)
        if data.get("created_at"):
            cmd.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("last_used"):
            cmd.last_used = datetime.fromisoformat(data["last_used"])
        return cmd

class SnippetCategory:
    def __init__(self, name: str, parent: Optional['SnippetCategory'] = None):
        self.name = name
        self.parent = parent
        self.commands: List[SnippetCommand] = []
        self.subcategories: List['SnippetCategory'] = []
        self.id = str(uuid.uuid4())
    
    def add_command(self, command: SnippetCommand):
        self.commands.append(command)
    
    def remove_command(self, command_id: str) -> bool:
        for i, cmd in enumerate(self.commands):
            if cmd.id == command_id:
                del self.commands[i]
                return True
        return False
    
    def add_subcategory(self, category: 'SnippetCategory'):
        category.parent = self
        self.subcategories.append(category)
    
    def remove_subcategory(self, category_name: str) -> bool:
        for i, cat in enumerate(self.subcategories):
            if cat.name == category_name:
                del self.subcategories[i]
                return True
        return False
    
    def get_full_path(self) -> str:
        if self.parent:
            return f"{self.parent.get_full_path()}/{self.name}"
        return self.name
    
    def find_command(self, command_id: str) -> Optional[SnippetCommand]:
        # Search in this category
        for cmd in self.commands:
            if cmd.id == command_id:
                return cmd
        
        # Search in subcategories
        for subcat in self.subcategories:
            found = subcat.find_command(command_id)
            if found:
                return found
        
        return None
    
    def search_commands(self, query: str) -> List[Tuple[SnippetCommand, str]]:
        results = []
        query_lower = query.lower()
        
        # Search in this category
        for cmd in self.commands:
            if (query_lower in cmd.content.lower() or 
                query_lower in cmd.description.lower()):
                results.append((cmd, self.get_full_path()))
        
        # Search in subcategories
        for subcat in self.subcategories:
            results.extend(subcat.search_commands(query))
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "id": self.id,
            "commands": [cmd.to_dict() for cmd in self.commands],
            "subcategories": [subcat.to_dict() for subcat in self.subcategories]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], parent: Optional['SnippetCategory'] = None):
        category = cls(data["name"], parent)
        category.id = data.get("id", str(uuid.uuid4()))
        
        # Load commands
        for cmd_data in data.get("commands", []):
            category.commands.append(SnippetCommand.from_dict(cmd_data))
        
        # Load subcategories
        for subcat_data in data.get("subcategories", []):
            category.subcategories.append(cls.from_dict(subcat_data, category))
        
        return category

class SnippetsManager:
    def __init__(self):
        self.root_categories: List[SnippetCategory] = []
        self._initialize_default_categories()
    
    def _initialize_default_categories(self):
        # Create default category structure
        ssh_cat = SnippetCategory("SSH")
        ssh_cat.add_command(SnippetCommand(
            "ssh -p var user@var", 
            "SSH connection with custom port",
            ["port", "hostname"]
        ))
        ssh_cat.add_command(SnippetCommand(
            "ssh-keygen -t rsa -b 4096 -C 'var'",
            "Generate SSH key with email",
            ["email"]
        ))
        
        docker_cat = SnippetCategory("Docker")
        docker_cat.add_command(SnippetCommand(
            "docker run -it --rm -p var:var var",
            "Run container with port mapping",
            ["host_port", "container_port", "image"]
        ))
        docker_cat.add_command(SnippetCommand(
            "docker exec -it var /bin/bash",
            "Execute bash in running container",
            ["container_name"]
        ))
        
        adb_cat = SnippetCategory("ADB")
        adb_cat.add_command(SnippetCommand(
            "adb connect var:5555",
            "Connect to device over TCP",
            ["device_ip"]
        ))
        adb_cat.add_command(SnippetCommand(
            "adb shell am start -n var/var",
            "Start Android activity",
            ["package", "activity"]
        ))
        
        git_cat = SnippetCategory("Git")
        git_cat.add_command(SnippetCommand(
            "git clone --branch var var",
            "Clone specific branch",
            ["branch", "repo_url"]
        ))
        
        self.root_categories = [ssh_cat, docker_cat, adb_cat, git_cat]
    
    def add_root_category(self, name: str) -> SnippetCategory:
        category = SnippetCategory(name)
        self.root_categories.append(category)
        return category
    
    def remove_root_category(self, name: str) -> bool:
        for i, cat in enumerate(self.root_categories):
            if cat.name == name:
                del self.root_categories[i]
                return True
        return False
    
    def find_category(self, path: str) -> Optional[SnippetCategory]:
        parts = path.split('/')
        if not parts:
            return None
        
        # Find root category
        root_name = parts[0]
        current_cat = None
        for cat in self.root_categories:
            if cat.name == root_name:
                current_cat = cat
                break
        
        if not current_cat:
            return None
        
        # Navigate through subcategories
        for part in parts[1:]:
            found = False
            for subcat in current_cat.subcategories:
                if subcat.name == part:
                    current_cat = subcat
                    found = True
                    break
            if not found:
                return None
        
        return current_cat
    
    def add_command_to_category(self, category_path: str, command: SnippetCommand) -> bool:
        category = self.find_category(category_path)
        if category:
            category.add_command(command)
            return True
        return False
    
    def find_command(self, command_id: str) -> Optional[Tuple[SnippetCommand, SnippetCategory]]:
        for root_cat in self.root_categories:
            cmd = root_cat.find_command(command_id)
            if cmd:
                return cmd, root_cat
        return None
    
    def search_all_commands(self, query: str) -> List[Tuple[SnippetCommand, str]]:
        results = []
        for root_cat in self.root_categories:
            results.extend(root_cat.search_commands(query))
        return results
    
    def get_category_tree(self) -> List[Dict[str, Any]]:
        return [cat.to_dict() for cat in self.root_categories]
    
    def load_from_dict(self, data: Dict[str, Any]):
        self.root_categories = []
        for cat_data in data.get("categories", []):
            self.root_categories.append(SnippetCategory.from_dict(cat_data))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "categories": [cat.to_dict() for cat in self.root_categories],
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat()
            }
        }
