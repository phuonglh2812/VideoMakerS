import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import os
import uuid
import asyncio
from typing import Optional

class TaskHistoryManager:
    def __init__(self, base_path):
        self.history_file = Path(base_path) / "task_history.json"
        self.max_history_days = 30  # Giữ lịch sử trong 30 ngày
        self.task_events = {}  # Store events for task completion
        self.max_wait_time = 30 * 60  # 30 minutes timeout
        
        # Tạo file mới nếu chưa tồn tại hoặc bị lỗi
        self._initialize_history_file()
    
    def _initialize_history_file(self):
        """Khởi tạo file history, xử lý các trường hợp file lỗi"""
        try:
            if self.history_file.exists():
                # Thử đọc file hiện tại
                try:
                    with open(self.history_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Initialize task events for existing tasks
                        for task_id, task_data in data.items():
                            if task_data.get('status') == 'processing':
                                self.task_events[task_id] = asyncio.Event()
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Nếu file lỗi, backup và tạo mới
                    backup_path = self.history_file.with_suffix('.json.bak')
                    try:
                        os.rename(self.history_file, backup_path)
                        logging.warning(f"Corrupted history file backed up to {backup_path}")
                    except Exception as e:
                        logging.error(f"Failed to backup corrupted history file: {e}")
                        # Nếu không backup được thì xóa luôn
                        os.remove(self.history_file)
                    
                    # Tạo file mới
                    self._create_new_history_file()
            else:
                # Tạo file mới nếu chưa tồn tại
                self._create_new_history_file()
                
        except Exception as e:
            logging.error(f"Error initializing task history: {e}")
            # Đảm bảo luôn có file history hợp lệ
            self._create_new_history_file()

    def _create_new_history_file(self):
        """Tạo file history mới với nội dung rỗng"""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2)
        except Exception as e:
            logging.error(f"Error creating new history file: {e}")
            raise
    
    def create_task(self, task_id: str, initial_status: dict):
        """Create a new task with initial status"""
        logging.info(f"Creating new task {task_id} with status {initial_status}")
        self.task_events[task_id] = asyncio.Event()
        self.save_task(task_id, initial_status)
        
    def save_task(self, task_id: str, task_data: dict):
        """Lưu thông tin task vào file history"""
        logging.info(f"Saving task {task_id} with data {task_data}")
        try:
            # Đọc history hiện tại
            history = self._read_history()
            logging.debug(f"Current history: {history}")
            
            # Thêm timestamp
            task_data['updated_at'] = datetime.now().isoformat()
            if 'created_at' not in task_data:
                task_data['created_at'] = task_data['updated_at']
            
            # Check if task is complete
            old_status = history.get(task_id, {}).get('status')
            new_status = task_data.get('status')
            
            # Lưu task
            history[task_id] = task_data
            
            # Xóa các task quá cũ
            self._cleanup_old_tasks(history)
            
            # Ghi lại file
            self._write_history(history)
            logging.info(f"Task {task_id} saved successfully")
            
            # Set event if task is complete
            if old_status == 'processing' and new_status in ['completed', 'error']:
                if task_id in self.task_events:
                    self.task_events[task_id].set()
                    
        except Exception as e:
            logging.error(f"Error saving task history: {e}")
            # Nếu có lỗi, thử khởi tạo lại file và lưu
            try:
                self._initialize_history_file()
                history = {task_id: task_data}
                self._write_history(history)
                logging.info(f"Task {task_id} saved after recovery")
            except Exception as e2:
                logging.error(f"Failed to recover and save task: {e2}")
    
    async def wait_for_task(self, task_id: str, timeout: int = 1800) -> dict:
        """Đợi cho đến khi task hoàn thành hoặc có lỗi
        Args:
            task_id (str): ID của task
            timeout (int): Thời gian timeout tính bằng giây, mặc định 30 phút
        Returns:
            dict: Task data
        Raises:
            asyncio.TimeoutError: Nếu quá thời gian timeout
        """
        import asyncio
        import time
        
        start_time = time.time()
        check_interval = 1  # Check mỗi giây
        
        while True:
            # Check if timeout
            if time.time() - start_time > timeout:
                raise asyncio.TimeoutError(f"Task {task_id} timeout after {timeout} seconds")
                
            # Get current status
            task = self.get_task(task_id)
            if task.get('status') == 'not_found':
                raise ValueError(f"Task {task_id} not found")
                
            # Return if task is completed or has error
            if task.get('status') in ['completed', 'error']:
                return task
                
            # Wait before next check
            await asyncio.sleep(check_interval)
    
    def get_task(self, task_id: str) -> dict:
        """Lấy thông tin task từ history"""
        try:
            history = self._read_history()
            return history.get(task_id, {"status": "not_found"})
        except Exception as e:
            logging.error(f"Error reading task history: {e}")
            return {"status": "not_found"}
    
    def _read_history(self) -> dict:
        """Đọc file history"""
        try:
            if not self.history_file.exists():
                self._create_new_history_file()
                return {}
                
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Nếu file lỗi, khởi tạo lại
            self._initialize_history_file()
            return {}
        except Exception as e:
            logging.error(f"Error reading history file: {e}")
            return {}
    
    def _write_history(self, history: dict):
        """Ghi file history"""
        try:
            # Ghi trực tiếp vào file history
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            logging.info(f"Task history saved to {self.history_file}")
            
        except Exception as e:
            logging.error(f"Error writing history file: {e}")
            raise
    
    def _cleanup_old_tasks(self, history: dict):
        """Xóa các task quá cũ"""
        now = datetime.now()
        history_copy = history.copy()
        
        for task_id, task_data in history_copy.items():
            try:
                # Dùng created_at thay vì saved_at
                created_at = datetime.fromisoformat(task_data.get('created_at', now.isoformat()))
                if now - created_at > timedelta(days=self.max_history_days):
                    del history[task_id]
            except (ValueError, TypeError) as e:
                logging.warning(f"Invalid date format for task {task_id}: {e}")
                # Giữ lại task nếu không parse được ngày
                
    def update_task_status(self, task_id: str, status: str, message: str = None, error: str = None, data: dict = None):
        """Update task status
        Args:
            task_id (str): ID của task
            status (str): Status mới (completed, error, processing)
            message (str, optional): Message mới. Defaults to None.
            error (str, optional): Error message nếu có lỗi. Defaults to None.
            data (dict, optional): Additional task data. Defaults to None.
        """
        logging.info(f"Updating task {task_id} status to {status}")
        try:
            # Get current task
            task = self.get_task(task_id)
            if task.get('status') == 'not_found':
                logging.error(f"Cannot update non-existent task {task_id}")
                return
                
            # Update task data
            task['status'] = status
            if message:
                task['message'] = message
            if error:
                task['error'] = error
            if data:
                task.update(data)
                
            # Save updated task
            self.save_task(task_id, task)
            logging.info(f"Task {task_id} status updated successfully")
            
        except Exception as e:
            logging.error(f"Error updating task status: {e}")
            raise
