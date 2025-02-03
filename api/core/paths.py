import os
from pathlib import Path

class PathManager:
    """
    Manage all paths in the application
    
    Directory structure:
    D:/SuaCode1/                  # base_path
    ├── Input_16_9/              # hook_maker: input_16_9 videos
    ├── input_9_16/              # hook_maker: input_9_16 videos
    ├── cut/                     # hook_maker: cut videos
    ├── used/                    # hook_maker: used videos
    ├── temp/                    # common: temp files (shared)
    ├── final/                   # common: final output (shared)
    ├── config/                  # config directory
    │   └── presets/            # common: subtitle presets (shared)
    ├── assets/                  # video_maker assets
    │   ├── audio/              # video_maker: audio files
    │   ├── srt/                # video_maker: subtitle files
    │   ├── overlay1/           # video_maker: overlay images 1
    │   └── overlay2/           # video_maker: overlay images 2
    └── output/                 # video_maker: output files
    
    Shared directories:
    - temp/: Temporary files used by both workflows
    - final/: Final output files from both workflows
    - config/presets/: Subtitle presets used by both workflows
    
    Hook maker specific:
    - Input_16_9/: Input directory for 16:9 videos
    - input_9_16/: Input directory for 9:16 videos
    - cut/: Directory for cut videos
    - used/: Directory for used videos
    
    Video maker specific:
    - assets/: Directory containing all input assets
      - audio/: Audio files
      - srt/: Subtitle files
      - overlay1/, overlay2/: Overlay images
    - output/: Output directory for processed videos
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize path manager
        Args:
            base_path: Đường dẫn gốc, mặc định là thư mục hiện tại
        """
        self.base_path = Path(base_path or os.getenv("BASE_PATH", "D:/AutomateWorkFlow/WorkflowFile/VideoMakerS_Files"))
        self.presets_path = self.base_path / "config/presets"  # Shared presets folder
        self._init_paths()
        
        # Create presets directory if it doesn't exist
        self.presets_path.mkdir(parents=True, exist_ok=True)
    
    def _init_paths(self):
        """Initialize all paths with environment variables or defaults"""
        # Common paths used across workflows
        self.common_paths = {
            "temp": "temp",
            "final": "final",
            "presets": "config/presets"  # Shared presets folder
        }
        
        # Video maker workflow paths
        self.video_maker_paths = {
            "audio": "assets/audio",
            "subtitle": "assets/srt",
            "overlay1": "assets/overlay1",
            "overlay2": "assets/overlay2",
            "output": "output",
            "temp": "temp",
            "final": "final",
            "presets": "config/presets"  # Use shared presets
        }
        
        # Hook maker workflow paths
        self.hook_maker_paths = {
            "input_16_9": "Input_16_9",  # For 16:9 videos
            "input_9_16": "input_9_16",  # For 9:16 videos
            "cut": "cut",
            "used": "used",
            "temp": "temp",
            "final": "final",
            "presets": "config/presets",  # Use shared presets
            "config": "config"
        }
        
        # Create directories if they don't exist
        self._create_directories()
    
    def _create_directories(self):
        """Create all required directories"""
        # Create common directories
        for path in self.common_paths.values():
            (self.base_path / path).mkdir(parents=True, exist_ok=True)
            
        # Create video maker directories
        for path in self.video_maker_paths.values():
            (self.base_path / path).mkdir(parents=True, exist_ok=True)
            
        # Create hook maker directories
        for path in self.hook_maker_paths.values():
            (self.base_path / path).mkdir(parents=True, exist_ok=True)
            
    def get_path(self, path_key: str, workflow: str = None) -> Path:
        """
        Get absolute path for a path key
        Args:
            path_key: Key of the path to get
            workflow: Optional workflow name to get path from
        Returns:
            Absolute Path object
        """
        if workflow == "video_maker":
            if path_key not in self.video_maker_paths:
                raise KeyError(f"Invalid path key for video_maker: {path_key}")
            relative_path = self.video_maker_paths[path_key]
        elif workflow == "hook_maker":
            if path_key not in self.hook_maker_paths:
                raise KeyError(f"Invalid path key for hook_maker: {path_key}")
            relative_path = self.hook_maker_paths[path_key]
        elif path_key == "presets":  # Special case for presets
            return self.presets_path
        else:
            if path_key not in self.common_paths:
                raise KeyError(f"Invalid common path key: {path_key}")
            relative_path = self.common_paths[path_key]
            
        return self.base_path / relative_path
        
    def get_workflow_paths(self, workflow: str) -> dict:
        """
        Get paths for a specific workflow
        Args:
            workflow: Tên workflow (video_maker, hook_maker)
        Returns:
            Dict chứa các đường dẫn của workflow
        """
        if workflow == "video_maker":
            paths = self.video_maker_paths
        elif workflow == "hook_maker":
            paths = self.hook_maker_paths
        else:
            paths = self.common_paths
            
        # Convert paths to absolute paths
        return {
            key: self.base_path / path
            for key, path in paths.items()
        }
    
    def get_path(self, workflow: str, path_key: str) -> Path:
        """
        Get a specific path from a workflow
        Args:
            workflow: Tên workflow (video_maker, hook_maker)
            path_key: Tên đường dẫn cần lấy
        Returns:
            Path object
        """
        paths = self.get_workflow_paths(workflow)
        if path_key not in paths:
            raise ValueError(f"Không tìm thấy đường dẫn '{path_key}' trong workflow '{workflow}'")
        return paths[path_key]
    
    def create_workflow_dirs(self, workflow: str):
        """
        Create all directories for a workflow
        Args:
            workflow: Tên workflow (video_maker, hook_maker)
        """
        paths = self.get_workflow_paths(workflow)
        for path in paths.values():
            path.mkdir(parents=True, exist_ok=True)
    
    def get_preset_path(self, preset_name: str) -> Path:
        """Get path to a specific preset file"""
        return self.presets_path / f"{preset_name}.json"

# Create singleton instance
path_manager = PathManager()

# Export path_manager instance
__all__ = ['path_manager']
