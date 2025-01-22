# Video Maker

Video Maker là ứng dụng tạo video từ audio và subtitle, với khả năng tùy chỉnh font chữ và thêm overlay.

## Cấu trúc thư mục

```
VideoMakerv1/
├── api/                    # FastAPI backend
│   ├── core/              # Core modules
│   │   ├── config.py      # Global settings
│   │   └── paths.py       # Path management
│   ├── presets/           # Subtitle presets
│   │   ├── 1.json
│   │   └── 2.json
│   └── workflows/         # API workflows
│       └── video_maker/   # Video maker workflow
│           ├── models.py  # Data models
│           ├── router.py  # API routes
│           └── service.py # Business logic
├── config/                # App configuration
│   └── settings.json      # Global settings
├── modules/              # Shared modules
│   ├── file/            # File management
│   │   └── file_manager.py
│   ├── utils/           # Utilities
│   │   ├── font_manager.py
│   │   └── settings_manager.py
│   └── video/           # Video processing
│       ├── processor.py
│       ├── subtitle_processor.py
│       ├── video_cache.py
│       ├── video_cutter.py
│       └── video_cutter_processor.py
├── makergui.py          # GUI application
└── requirements.txt     # Python dependencies
```

## Cấu trúc thư mục làm việc

```
D:/SuaCode1/                  # Thư mục gốc
├── Input_16_9/              # Hook maker: Input video 16:9
├── input_9_16/              # Hook maker: Input video 9:16
├── cut/                     # Hook maker: Video đã cắt
├── used/                    # Hook maker: Video đã sử dụng
├── temp/                    # Chung: File tạm thời
├── final/                   # Chung: File đầu ra cuối cùng
├── config/                  # Thư mục cấu hình
│   └── presets/            # Chung: Preset phụ đề
├── assets/                  # Video maker: Asset đầu vào
│   ├── audio/              # Video maker: File audio
│   ├── srt/                # Video maker: File phụ đề
│   ├── overlay1/           # Video maker: Ảnh overlay 1
│   └── overlay2/           # Video maker: Ảnh overlay 2
└── output/                 # Video maker: File đầu ra

Thư mục dùng chung:
- temp/: File tạm thời của cả hai workflow
- final/: File đầu ra cuối cùng của cả hai workflow
- config/presets/: Preset phụ đề dùng chung

Thư mục riêng Hook maker:
- Input_16_9/: Thư mục chứa video input tỉ lệ 16:9
- input_9_16/: Thư mục chứa video input tỉ lệ 9:16
- cut/: Thư mục chứa video đã cắt
- used/: Thư mục chứa video đã sử dụng

Thư mục riêng Video maker:
- assets/: Thư mục chứa tất cả asset đầu vào
  - audio/: File audio
  - srt/: File phụ đề
  - overlay1/, overlay2/: Ảnh overlay
- output/: Thư mục chứa video đầu ra
```

## Cài đặt

1. Cài đặt Python dependencies:
```bash
pip install -r requirements.txt
```

2. Cấu hình trong `config/settings.json`:
```json
{
    "common": {
        "base_path": ".",
        "log_level": "INFO"
    },
    "workflows": {
        "video_maker": {
            "input_dir": "raw",
            "output_dir": "output",
            "temp_dir": "temp",
            "cut_dir": "cut",
            "video_settings": {
                "width": 1920,
                "height": 1080,
                "fps": 30
            }
        }
    }
}
```

## Sử dụng

### API

1. Khởi động API server:
```bash
uvicorn api.main:app --reload --port 5001
```

2. API Endpoints:
- `POST /api/process/make`: Tạo video từ audio và subtitle
  ```bash
  curl -X POST 'http://localhost:5001/api/process/make' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'audio_path=path/to/audio.wav&subtitle_path=path/to/subtitle.srt&preset_name=1'
  ```

### GUI

1. Khởi động GUI app:
```bash
python makergui.py
```

2. Các tính năng:
- Video Maker: Tạo video từ audio và subtitle
- Video Cutter: Cắt video thành các đoạn ngắn
- Preset Manager: Quản lý cấu hình subtitle

## Preset

Preset được lưu trong `api/presets/` với định dạng JSON:
```json
{
    "font_name": "Arial",
    "font_size": 30,
    "primary_color": "&HFFFFFF&",
    "outline_color": "&H000000&",
    "back_color": "&H000000&",
    "outline_width": 2.0,
    "shadow_width": 0.0,
    "margin_v": 20,
    "margin_h": 20,
    "alignment": 2,
    "max_chars": 40
}
```

## Dependencies

- Python 3.8+
- FFmpeg
- MoviePy
- FastAPI
- pysubs2
- tkinter (cho GUI)

## Troubleshooting

1. Font không tìm thấy:
- Kiểm tra font đã được cài đặt trong Windows
- Sử dụng font mặc định (Arial) trong preset

2. Video processing lỗi:
- Kiểm tra FFmpeg đã được cài đặt
- Kiểm tra đường dẫn file input tồn tại
- Xem log để biết chi tiết lỗi
