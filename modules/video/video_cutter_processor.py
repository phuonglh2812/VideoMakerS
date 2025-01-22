import logging
from pathlib import Path
from typing import List, Dict, Optional
from .video_cutter import VideoCutter
from modules.file.file_manager import FileManager

class VideoCutterProcessor:
    def __init__(self, raw_dir: Path, cut_dir: Path):
        """Khởi tạo processor để cắt video từ raw thành các segment"""
        self.raw_dir = Path(raw_dir)
        self.cut_dir = Path(cut_dir)
        self.file_manager = FileManager(
            base_path=self.raw_dir.parent,
            paths={
                'raw': self.raw_dir,
                'cut': self.cut_dir,
                'used': self.raw_dir.parent / 'used'
            }
        )
        self.video_cutter = VideoCutter(self.cut_dir)

    def process_raw_videos(self, min_duration: float = 4.0, max_duration: float = 7.0) -> List[Path]:
        """
        Xử lý tất cả video trong thư mục raw
        Args:
            min_duration: Độ dài tối thiểu của mỗi segment (giây)
            max_duration: Độ dài tối đa của mỗi segment (giây)
        Returns:
            List[Path]: Danh sách đường dẫn tới các file đã xử lý
        """
        # Get list of raw videos
        raw_videos = list(self.raw_dir.glob("*.mp4"))
        if not raw_videos:
            logging.warning("No raw videos found in directory")
            return []

        processed_files = []
        for video in raw_videos:
            try:
                # Cut video into segments
                segments = self.video_cutter.cut_video(
                    video,
                    min_duration=min_duration,
                    max_duration=max_duration
                )
                processed_files.extend(segments)
                
                # Move original video to used directory
                self.file_manager.move_to_used(video)
                
            except Exception as e:
                logging.error(f"Error processing video {video}: {str(e)}")
                continue

        return processed_files
