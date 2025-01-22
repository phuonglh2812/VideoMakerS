import json
from pathlib import Path
from typing import Dict, Any
from .paths import PathManager

class Settings:
    """Global settings handler"""
    def __init__(self):
        self.path_manager = PathManager()
        self.config_path = self.path_manager.base_path / "config/settings.json"
        self.settings = self._load_settings()
        
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file"""
        if not self.config_path.exists():
            return {"common": {}, "workflows": {}}
        
        with open(self.config_path, "r") as f:
            return json.load(f)
    
    def get_common_settings(self) -> Dict[str, Any]:
        """Get common settings"""
        return self.settings.get("common", {})
    
    def get_workflow_settings(self, workflow_name: str) -> Dict[str, Any]:
        """Get settings for specific workflow"""
        workflows = self.settings.get("workflows", {})
        return workflows.get(workflow_name, {})
    
    @property
    def PROJECT_NAME(self) -> str:
        return self.get_common_settings().get("project_name", "Video Maker API")
        
    @property
    def VERSION(self) -> str:
        return self.get_common_settings().get("version", "1.0.0")
        
    @property
    def HOST(self) -> str:
        return self.get_common_settings().get("host", "0.0.0.0")
        
    @property
    def PORT(self) -> int:
        return self.get_common_settings().get("port", 5001)
        
    @property
    def API_KEY(self) -> str:
        return self.get_common_settings().get("api_key", "your-api-key")
