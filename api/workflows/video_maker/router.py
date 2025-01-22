from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form
from typing import Optional
from .models import MakeVideoRequest, VideoResponse, ProcessingStatus
from .service import VideoMakerService
import uuid

class VideoMakerRouter:
    def __init__(self):
        self.router = APIRouter(prefix="/api/process", tags=["Process"])
        self.service = VideoMakerService()
        self._setup_routes()

    def _setup_routes(self):
        """Setup all routes for video maker"""
        @self.router.post("/make", response_model=VideoResponse)
        async def make_final_video(
            background_tasks: BackgroundTasks,
            request: Optional[str] = Form(None),
            audio_path: Optional[str] = Form(None),
            subtitle_path: Optional[str] = Form(None),
            overlay1_path: Optional[str] = Form(None),
            overlay2_path: Optional[str] = Form(None),
            preset_name: Optional[str] = Form(None),
            output_name: Optional[str] = Form(None)
        ) -> VideoResponse:
            """
            Create final video with:
            - Audio
            - Subtitles
            - Overlays (optional)
            - Preset settings
            """
            try:
                result = await self.service.make_final_video(
                    background_tasks=background_tasks,
                    request=request,
                    audio_path=audio_path,
                    subtitle_path=subtitle_path,
                    overlay1_path=overlay1_path,
                    overlay2_path=overlay2_path,
                    preset_name=preset_name,
                    output_name=output_name
                )
                return VideoResponse(**result)
            except Exception as e:
                return VideoResponse(
                    task_id=str(uuid.uuid4()),
                    status="error",
                    message=str(e),
                    error=str(e)
                )

        @self.router.get("/status/{task_id}", response_model=ProcessingStatus)
        async def get_process_status(task_id: str) -> ProcessingStatus:
            """Get processing status for a task"""
            status = await self.service.get_task_status(task_id)
            if status["status"] == "not_found":
                raise HTTPException(status_code=404, detail="Task not found")
            return ProcessingStatus(**status)

    def __call__(self):
        """Return the router when called"""
        return self.router
