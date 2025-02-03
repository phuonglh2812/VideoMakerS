import os
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict
import uuid
import json
from datetime import datetime
import logging
import asyncio

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from api.workflows.video_maker.router import VideoMakerRouter
from api.core.config import Settings
from api.core.paths import PathManager
from modules.file.file_manager import FileManager
from modules.utils.settings_manager import SettingsManager
from modules.utils.task_history_manager import TaskHistoryManager
from modules.video.hook_video_processor import HookVideoProcessor

# Initialize settings and paths
settings = Settings()
path_manager = PathManager()

# Initialize processors and managers
video_maker = VideoMakerRouter()
settings_manager = SettingsManager()  # SettingsManager uses path_manager internally
hook_processor = HookVideoProcessor(path_manager.base_path)
file_manager = FileManager(path_manager.base_path)
task_history = TaskHistoryManager(path_manager.base_path)  # Use base_path from path_manager

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for creating videos with audio, subtitles and overlays",
    version=settings.VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add video maker router
app.include_router(video_maker.router, prefix="/api/v1")

def update_task_status(task_id: str, status: str, message: str = None, error: str = None):
    """Update task status in history"""
    task_data = {
        "task_id": task_id,
        "status": status,
        "message": message,
        "error": error
    }
    task_history.save_task(task_id, task_data)

def create_task(initial_status: dict) -> str:
    """Create a new task with initial status"""
    task_id = str(uuid.uuid4())
    task_history.create_task(task_id, initial_status)
    return task_id

# Hook API endpoints
@app.post("/api/v1/hook/process")
async def process_hook_video(
    background_tasks: BackgroundTasks,
    hook_audio: UploadFile = File(...),
    main_audio: UploadFile = File(...),
    subtitle_file: UploadFile = File(...),
    thumbnail_file: UploadFile = File(...),
    preset_name: Optional[str] = Form(None),
    subtitle_settings: Optional[str] = Form(None),
    is_vertical: bool = Form(False)
):
    task_id = create_task({"status": "processing", "message": "Task started successfully"})
    try:
        # Save uploaded files
        hook_path = await file_manager.save_upload(hook_audio, "temp")
        main_path = await file_manager.save_upload(main_audio, "temp")
        subtitle_path = await file_manager.save_upload(subtitle_file, "temp")
        thumbnail_path = await file_manager.save_upload(thumbnail_file, "temp")

        # Get subtitle settings
        if preset_name:
            subtitle_settings = settings_manager.load_preset(preset_name)
        elif subtitle_settings:
            subtitle_settings = json.loads(subtitle_settings)
        else:
            raise HTTPException(status_code=400, detail="Either preset_name or subtitle_settings is required")

        # Process video in background
        background_tasks.add_task(
            hook_processor.process_hook_video_background,
            task_id,
            hook_path,
            main_path,
            subtitle_path,
            thumbnail_path,
            subtitle_settings,
            is_vertical
        )

        return {
            "task_id": task_id,
            "status": "processing",
            "message": "Task started successfully"
        }
    except Exception as e:
        update_task_status(task_id, "error", error=str(e))
        return {
            "task_id": task_id,
            "status": "error",
            "error": str(e)
        }

@app.post("/api/v1/hook/batch/16_9")
async def process_batch_hooks_16_9(
    background_tasks: BackgroundTasks,
    input_folder: str = Form(...),
    preset_name: str = Form(...)
):
    """
    Xử lý batch video hook với tỉ lệ 16:9
    Args:
        input_folder: Thư mục chứa các file đầu vào
        preset_name: Tên preset cài đặt phụ đề
    """
    try:
        # Validate input folder
        input_path = Path(input_folder)
        if not input_path.exists():
            raise HTTPException(status_code=400, detail=f"Thư mục không tồn tại: {input_folder}")

        # Get subtitle settings from preset
        subtitle_settings = settings_manager.load_preset(preset_name)
        if not subtitle_settings:
            raise HTTPException(status_code=400, detail=f"Không tìm thấy preset: {preset_name}")

        # Create task after validation
        task_id = create_task({
            "status": "processing",
            "message": "Đang xử lý batch video 16:9"
        })

        # Process videos in background
        background_tasks.add_task(
            hook_processor.process_batch_videos_background,
            task_id,
            input_path,
            subtitle_settings,
            is_vertical=False  # 16:9 video
        )

        return {
            "task_id": task_id,
            "status": "processing",
            "message": "Đang xử lý batch video 16:9"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Lỗi khi xử lý batch video 16:9: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/hook/batch/9_16")
async def process_batch_hooks_9_16(
    background_tasks: BackgroundTasks,
    input_folder: str = Form(...),
    preset_name: str = Form(...)
):
    """
    Xử lý batch video hook với tỉ lệ 9:16
    Args:
        input_folder: Thư mục chứa các file đầu vào
        preset_name: Tên preset cài đặt phụ đề
    """
    try:
        # Validate input folder
        input_path = Path(input_folder)
        if not input_path.exists():
            raise HTTPException(status_code=400, detail=f"Thư mục không tồn tại: {input_folder}")

        # Get subtitle settings from preset
        subtitle_settings = settings_manager.load_preset(preset_name)
        if not subtitle_settings:
            raise HTTPException(status_code=400, detail=f"Không tìm thấy preset: {preset_name}")

        # Create task after validation
        task_id = create_task({
            "status": "processing",
            "message": "Đang xử lý batch video 9:16"
        })

        # Process videos in background
        background_tasks.add_task(
            hook_processor.process_batch_videos_background,
            task_id,
            input_path,
            subtitle_settings,
            is_vertical=True  # 9:16 video
        )

        return {
            "task_id": task_id,
            "status": "processing",
            "message": "Đang xử lý batch video 9:16"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Lỗi khi xử lý batch video 9:16: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/hook/status/{task_id}")
async def get_hook_status(task_id: str):
    """Get status of a hook processing task"""
    try:
        # Get current task status
        status = task_history.get_task(task_id)
        
        # If task not found, return 404
        if status.get('status') == 'not_found':
            raise HTTPException(
                status_code=404, 
                detail=f"Task {task_id} not found"
            )
            
        # If task is completed or has error, return immediately
        if status.get('status') in ['completed', 'error']:
            return status
            
        # If task is still processing, wait for completion or error
        try:
            # Wait for task to complete with 30 minute timeout
            status = await task_history.wait_for_task(task_id)
            return status
            
        except asyncio.TimeoutError:
            logging.warning(f"Timeout waiting for task {task_id}")
            raise HTTPException(
                status_code=408,  # Request Timeout
                detail=f"Task {task_id} processing timeout after 30 minutes"
            )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error getting hook status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/hook/presets")
async def get_presets():
    return settings_manager.get_presets()

@app.post("/api/v1/hook/presets")
async def create_preset(
    preset_name: str = Form(...),
    settings: str = Form(...)
):
    try:
        settings_dict = json.loads(settings)
        settings_manager.save_preset(preset_name, settings_dict)
        return {"message": f"Preset {preset_name} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/v1/hook/presets/{preset_name}")
async def delete_preset(preset_name: str):
    try:
        settings_manager.delete_preset(preset_name)
        return {"message": f"Preset {preset_name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
