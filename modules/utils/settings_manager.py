import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from api.core.paths import path_manager

class SettingsManager:
    def __init__(self):
        """Khởi tạo SettingsManager"""
        # Dùng presets path từ path_manager, presets nằm trong common_paths
        self.presets_dir = path_manager.base_path / "config/presets"
        self._ensure_presets_dir()
        
    def _ensure_presets_dir(self):
        """Đảm bảo thư mục presets tồn tại"""
        try:
            self.presets_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logging.error(f"Lỗi khi tạo thư mục presets: {e}")
            
    def _get_preset_file(self, name: str) -> Path:
        """Lấy đường dẫn file preset"""
        return self.presets_dir / f"{name}.json"
            
    def save_preset(self, name: str, settings: Dict) -> bool:
        """
        Lưu một preset mới vào file riêng
        Args:
            name (str): Tên preset
            settings (Dict): Cài đặt của preset
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            preset_file = self._get_preset_file(name)
            with open(preset_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Lỗi khi lưu preset {name}: {e}")
            return False
            
    def load_preset(self, name: str) -> Optional[Dict]:
        """
        Load một preset từ file
        Args:
            name (str): Tên preset
        Returns:
            Optional[Dict]: Cài đặt của preset hoặc None nếu không tồn tại
        """
        try:
            preset_file = self._get_preset_file(name)
            if preset_file.exists():
                with open(preset_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle nested structure with "1" key
                    if isinstance(data, dict) and "1" in data:
                        return data["1"]
                    return data
            return None
        except Exception as e:
            logging.error(f"Lỗi khi load preset {name}: {e}")
            return None
            
    def delete_preset(self, name: str) -> bool:
        """
        Xóa một preset
        Args:
            name (str): Tên preset cần xóa
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            preset_file = self._get_preset_file(name)
            if preset_file.exists():
                preset_file.unlink()
            return True
        except Exception as e:
            logging.error(f"Lỗi khi xóa preset {name}: {e}")
            return False
            
    def get_presets(self) -> List[str]:
        """
        Lấy danh sách tên các preset có sẵn
        Returns:
            List[str]: Danh sách tên các preset
        """
        try:
            return [f.stem for f in self.presets_dir.glob("*.json")]
        except Exception as e:
            logging.error(f"Lỗi khi lấy danh sách presets: {e}")
            return []
            
    def get_preset_content(self, name: str) -> Optional[Dict]:
        """
        Lấy nội dung của một preset
        Args:
            name (str): Tên preset
        Returns:
            Optional[Dict]: Nội dung preset hoặc None nếu không tồn tại
        """
        return self.load_preset(name)
