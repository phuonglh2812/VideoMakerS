import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from fastapi import HTTPException, BackgroundTasks
from api.core.paths import path_manager
from modules.video.processor import VideoProcessor
from modules.utils.settings_manager import SettingsManager

class VideoMakerService:
    def __init__(self):
        """Initialize service with video processor"""
        self.video_processor = VideoProcessor(
            base_path=path_manager.base_path,
            paths=path_manager.get_workflow_paths("video_maker")
        )
        self.settings_manager = SettingsManager()  # Dùng settings manager để load preset
        self._task_status = {}  # Store task status in memory
        
    def _load_preset(self, preset_name: str) -> dict:
        """Load subtitle preset from file"""
        preset = self.settings_manager.load_preset(preset_name)
        if preset is None:
            raise HTTPException(
                status_code=404,
                detail=f"Preset {preset_name} not found"
            )
        return preset
    
    def update_task_status(self, task_id: str, status: Dict):
        """Update task status"""
        self._task_status[task_id] = status
        
    async def get_task_status(self, task_id: str) -> Dict:
        """Get task status"""
        return self._task_status.get(task_id, {"status": "not_found"})
        
    async def make_final_video(
        self,
        background_tasks: BackgroundTasks,
        request: Optional[str] = None,
        audio_path: Optional[str] = None,
        subtitle_path: Optional[str] = None,
        overlay1_path: Optional[str] = None,
        overlay2_path: Optional[str] = None,
        preset_name: Optional[str] = None,
        output_name: Optional[str] = None
    ) -> Dict:
        """Create final video with audio, subtitles and overlays"""
        try:
            # Generate task ID
            task_id = str(uuid.uuid4())
            
            # Parse request if provided
            if request:
                try:
                    request_data = json.loads(request)
                    audio_path = request_data.get('audio_path', audio_path)
                    subtitle_path = request_data.get('subtitle_path', subtitle_path)
                    overlay1_path = request_data.get('overlay1_path', overlay1_path)
                    overlay2_path = request_data.get('overlay2_path', overlay2_path)
                    preset_name = request_data.get('preset_name', preset_name)
                    output_name = request_data.get('output_name', output_name)
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail="Invalid JSON in request")
            
            # Validate required parameters
            if not all([audio_path, subtitle_path, preset_name]):
                raise HTTPException(
                    status_code=400,
                    detail="Missing required parameters: audio_path, subtitle_path, preset_name"
                )
                
            # Load preset
            subtitle_config = self._load_preset(preset_name)
                
            # Convert paths to Path objects and remove quotes if present
            paths = {
                'audio': Path(audio_path.strip('"')),
                'subtitle': Path(subtitle_path.strip('"')),
                'overlay1': Path(overlay1_path.strip('"')) if overlay1_path else None,
                'overlay2': Path(overlay2_path.strip('"')) if overlay2_path else None
            }
            
            # Validate all files exist
            for name, path in paths.items():
                if path and not path.exists():
                    raise HTTPException(
                        status_code=404,
                        detail=f"{name} file not found: {path}"
                    )
                    
            # Initialize status
            self.update_task_status(task_id, {
                "status": "processing",
                "progress": 0,
                "message": "Starting video processing",
                "created_at": datetime.now().isoformat(),
                "input_files": {
                    "audio": str(paths['audio']),
                    "subtitle": str(paths['subtitle']),
                    "overlay1": str(paths['overlay1']) if paths['overlay1'] else None,
                    "overlay2": str(paths['overlay2']) if paths['overlay2'] else None,
                }
            })
            
            # Start processing in background
            background_tasks.add_task(
                self._make_video_background,
                task_id=task_id,
                output_name=output_name,
                audio_path=paths['audio'],
                subtitle_path=paths['subtitle'],
                overlay1_path=paths['overlay1'],
                overlay2_path=paths['overlay2'],
                subtitle_config=subtitle_config
            )
            
            return {
                "task_id": task_id,
                "status": "processing",
                "message": "Video processing started",
                "output_path": None,
                "error": None
            }
            
        except Exception as e:
            logging.error(f"Error in make_final_video: {str(e)}")
            return {
                "task_id": str(uuid.uuid4()),
                "status": "error",
                "message": str(e),
                "output_path": None,
                "error": str(e)
            }
            
    async def _make_video_background(
        self,
        task_id: str,
        output_name: Optional[str] = None,
        audio_path: Optional[Path] = None,
        subtitle_path: Optional[Path] = None,
        overlay1_path: Optional[Path] = None,
        overlay2_path: Optional[Path] = None,
        subtitle_config: Optional[dict] = None
    ):
        """Process video in background"""
        try:
            # Update status
            self.update_task_status(task_id, {
                "status": "processing",
                "progress": 10,
                "message": "Processing video"
            })
            
            # Process video
            output_path = self.video_processor.process_video(
                audio_path=audio_path,
                subtitle_path=subtitle_path,
                overlay1_path=overlay1_path,
                overlay2_path=overlay2_path,
                subtitle_config=subtitle_config,
                output_name=output_name
            )
            
            # Update status on success
            self.update_task_status(task_id, {
                "status": "completed",
                "progress": 100,
                "message": "Video processing completed",
                "output_path": str(output_path),
                "completed_at": datetime.now().isoformat()
            })
            
        except Exception as e:
            logging.error(f"Error in make_video_background: {str(e)}")
            self.update_task_status(task_id, {
                "status": "error",
                "progress": 0,
                "message": str(e),
                "error_at": datetime.now().isoformat()
            })
