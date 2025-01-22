import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from pathlib import Path
import json
import logging
from modules.file.file_manager import FileManager
from modules.video.video_cutter import VideoCutter
from modules.video.processor import VideoProcessor
from modules.video.subtitle_processor import SubtitleProcessor
from modules.video.video_cutter_processor import VideoCutterProcessor
from api.core.paths import path_manager
from typing import Optional
import os

class VideoMakerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Maker")
        
        # Initialize paths using path_manager
        self.base_path = path_manager.base_path
        self.paths = path_manager.get_workflow_paths("video_maker")
        self.raw_dir = self.paths.get('raw', self.base_path / 'raw')
        self.cut_dir = self.paths.get('cut', self.base_path / 'cut')
        
        # Initialize file manager with specific directories
        self.file_manager = FileManager(
            base_path=self.base_path,
            paths=self.paths
        )
        
        # Initialize processors
        self.video_processor = VideoProcessor(
            base_path=self.base_path,
            paths=self.paths
        )
        self.video_cutter = VideoCutterProcessor(
            raw_dir=self.raw_dir,
            cut_dir=self.cut_dir
        )
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        # Main tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Video Maker")
        
        # Video Cutter tab
        self.cutter_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.cutter_tab, text="Video Cutter")
        
        # Default subtitle settings
        self.subtitle_settings = {
            'font_name': 'Arial',
            'font_size': 48,
            'primary_color': '&HFFFFFF&',
            'outline_color': '&H000000&',
            'back_color': '&H000000&',
            'outline_width': 2,
            'shadow_width': 0,
            'margin_v': 20,
            'margin_h': 20,
            'alignment': 2,
            'max_chars': 40
        }
        
        # Load saved settings if exists
        self.load_settings()
        
        # Initialize variables
        self.audio_path = tk.StringVar()
        self.subtitle_path = tk.StringVar()
        self.overlay1_path = tk.StringVar()
        self.overlay2_path = tk.StringVar()
        
        self.font_var = tk.StringVar(value=self.subtitle_settings['font_name'])
        self.font_size_var = tk.StringVar(value=str(self.subtitle_settings['font_size']))
        self.primary_color_var = tk.StringVar(value=self.subtitle_settings['primary_color'])
        self.outline_color_var = tk.StringVar(value=self.subtitle_settings['outline_color'])
        self.back_color_var = tk.StringVar(value=self.subtitle_settings['back_color'])
        self.outline_width_var = tk.StringVar(value=str(self.subtitle_settings['outline_width']))
        self.shadow_width_var = tk.StringVar(value=str(self.subtitle_settings['shadow_width']))
        self.margin_v_var = tk.StringVar(value=str(self.subtitle_settings['margin_v']))
        self.margin_h_var = tk.StringVar(value=str(self.subtitle_settings['margin_h']))
        self.alignment_var = tk.StringVar(value=str(self.subtitle_settings['alignment']))
        self.max_chars_var = tk.StringVar(value=str(self.subtitle_settings['max_chars']))
        
        self.preset_var = tk.StringVar()
        self.new_preset_var = tk.StringVar()
        
        self.min_duration_var = tk.StringVar(value="4.0")
        self.max_duration_var = tk.StringVar(value="7.0")
        
        self.setup_ui()
        
        self.init_settings_manager()
        
    def setup_ui(self):
        """Setup main UI"""
        # Setup main tab
        self.setup_main_tab()
        
        # Setup video cutter tab
        self.setup_cutter_tab()
    
    def setup_main_tab(self):
        """Setup main video maker tab"""
        main_frame = ttk.Frame(self.main_tab, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File selection
        self.setup_file_frame(main_frame)
        
        # Subtitle settings
        self.setup_subtitle_frame(main_frame)
        
        # Preset settings
        preset_frame = ttk.LabelFrame(self.main_tab, text="Preset Settings", padding="5 5 5 5")
        preset_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        
        # Combobox cho preset
        self.preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var)
        self.preset_combo.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.preset_combo.bind('<<ComboboxSelected>>', self.load_selected_preset)
        
        # Entry cho tên preset mới
        preset_name_entry = ttk.Entry(preset_frame, textvariable=self.new_preset_var)
        preset_name_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Buttons cho preset
        ttk.Button(preset_frame, text="Save Preset", command=self.save_preset).grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(preset_frame, text="Delete Preset", command=self.delete_preset).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Process button
        ttk.Button(main_frame, text="Process Video", 
                  command=self.process_video).grid(row=2, column=0, pady=10)
    
    def setup_cutter_tab(self):
        """Setup video cutter tab"""
        cutter_frame = ttk.Frame(self.cutter_tab, padding="10")
        cutter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Info frame
        info_frame = ttk.LabelFrame(cutter_frame, text="Directory Info", padding="5")
        info_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
        # Raw directory info
        ttk.Label(info_frame, text="Raw Directory:").grid(row=0, column=0, sticky=tk.W)
        self.raw_count_label = ttk.Label(info_frame, text="0 videos")
        self.raw_count_label.grid(row=0, column=1, padx=5)
        
        # Cut directory info
        ttk.Label(info_frame, text="Cut Directory:").grid(row=1, column=0, sticky=tk.W)
        self.cut_count_label = ttk.Label(info_frame, text="0 videos")
        self.cut_count_label.grid(row=1, column=1, padx=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(cutter_frame, text="Cutting Settings", padding="5")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        # Min duration
        ttk.Label(settings_frame, text="Min Duration (s):").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.min_duration_var, width=10).grid(row=0, column=1, padx=5)
        
        # Max duration
        ttk.Label(settings_frame, text="Max Duration (s):").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.max_duration_var, width=10).grid(row=1, column=1, padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(cutter_frame)
        buttons_frame.grid(row=2, column=0, sticky="ew", pady=5)
        
        # Process button
        ttk.Button(buttons_frame, text="Process Raw Videos", 
                  command=self.process_raw_videos).grid(row=0, column=0, padx=5)
        
        # Refresh button
        ttk.Button(buttons_frame, text="Refresh Counts", 
                  command=self.refresh_video_counts).grid(row=0, column=1, padx=5)
        
        # Initial refresh
        self.refresh_video_counts()
    
    def setup_file_frame(self, parent):
        """Setup file selection frame"""
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding="5")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Audio file
        ttk.Label(file_frame, text="Audio:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(file_frame, textvariable=self.audio_path).grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(file_frame, text="Browse", 
                  command=lambda: self.browse_file(self.audio_path, [("Audio Files", "*.mp3")])).grid(row=0, column=2)
        
        # Subtitle file
        ttk.Label(file_frame, text="Subtitle:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(file_frame, textvariable=self.subtitle_path).grid(row=1, column=1, sticky=(tk.W, tk.E))
        ttk.Button(file_frame, text="Browse", 
                  command=lambda: self.browse_file(self.subtitle_path, [("Subtitle Files", "*.srt")])).grid(row=1, column=2)
        
        # Overlay files
        ttk.Label(file_frame, text="Overlay 1:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(file_frame, textvariable=self.overlay1_path).grid(row=2, column=1, sticky=(tk.W, tk.E))
        ttk.Button(file_frame, text="Browse", 
                  command=lambda: self.browse_file(self.overlay1_path, [("Image Files", "*.png *.jpg")])).grid(row=2, column=2)
        
        ttk.Label(file_frame, text="Overlay 2:").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(file_frame, textvariable=self.overlay2_path).grid(row=3, column=1, sticky=(tk.W, tk.E))
        ttk.Button(file_frame, text="Browse", 
                  command=lambda: self.browse_file(self.overlay2_path, [("Image Files", "*.png *.jpg")])).grid(row=3, column=2)
        
    def setup_subtitle_frame(self, parent):
        """Setup subtitle settings frame"""
        subtitle_frame = ttk.LabelFrame(parent, text="Subtitle Settings")
        subtitle_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        # Font settings
        font_frame = ttk.Frame(subtitle_frame)
        font_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(font_frame, text="Font:").pack(side="left")
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_var)
        font_combo['values'] = self.get_system_fonts()
        font_combo.pack(side="left", padx=5)
        
        ttk.Label(font_frame, text="Size:").pack(side="left", padx=(10,0))
        ttk.Entry(font_frame, textvariable=self.font_size_var, width=5).pack(side="left", padx=5)

        # Color settings
        color_frame = ttk.Frame(subtitle_frame)
        color_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(color_frame, text="Text Color", 
                  command=lambda: self.choose_color(self.primary_color_var)).pack(side="left", padx=5)
        ttk.Button(color_frame, text="Outline Color", 
                  command=lambda: self.choose_color(self.outline_color_var)).pack(side="left", padx=5)
        ttk.Button(color_frame, text="Background Color", 
                  command=lambda: self.choose_color(self.back_color_var)).pack(side="left", padx=5)

        # Style settings
        style_frame = ttk.Frame(subtitle_frame)
        style_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(style_frame, text="Outline:").pack(side="left")
        ttk.Entry(style_frame, textvariable=self.outline_width_var, width=5).pack(side="left", padx=5)
        
        ttk.Label(style_frame, text="Shadow:").pack(side="left", padx=(10,0))
        ttk.Entry(style_frame, textvariable=self.shadow_width_var, width=5).pack(side="left", padx=5)

        # Margin settings
        margin_frame = ttk.Frame(subtitle_frame)
        margin_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(margin_frame, text="V-Margin:").pack(side="left")
        ttk.Entry(margin_frame, textvariable=self.margin_v_var, width=5).pack(side="left", padx=5)
        
        ttk.Label(margin_frame, text="H-Margin:").pack(side="left", padx=(10,0))
        ttk.Entry(margin_frame, textvariable=self.margin_h_var, width=5).pack(side="left", padx=5)

        # Alignment and max chars
        align_frame = ttk.Frame(subtitle_frame)
        align_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(align_frame, text="Alignment:").pack(side="left")
        align_combo = ttk.Combobox(align_frame, textvariable=self.alignment_var, width=5)
        align_combo['values'] = list(range(1, 10))
        align_combo.pack(side="left", padx=5)
        
        ttk.Label(align_frame, text="Max chars:").pack(side="left", padx=(10,0))
        ttk.Entry(align_frame, textvariable=self.max_chars_var, width=5).pack(side="left", padx=5)
        
        # Save settings button
        ttk.Button(subtitle_frame, text="Save Settings", 
                  command=self.save_settings).pack(pady=10)
                  
    def browse_file(self, path_var, filetypes):
        """Open file browser dialog"""
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            path_var.set(filename)
            
    def choose_color(self, color_var):
        """Open color picker and update color variable"""
        current_color = color_var.get()
        
        # Convert ASS color (&HBBGGRR&) to RGB hex (#RRGGBB)
        if current_color.startswith('&H') and current_color.endswith('&'):
            # Remove &H and & from start and end
            bgr = current_color[2:-1]
            if len(bgr) == 6:
                b, g, r = bgr[:2], bgr[2:4], bgr[4:]
                rgb_color = f'#{r}{g}{b}'
            else:
                rgb_color = '#FFFFFF'
        else:
            rgb_color = '#FFFFFF'
            
        color = colorchooser.askcolor(color=rgb_color)[1]
        if color:
            # Convert RGB hex (#RRGGBB) to ASS color (&HBBGGRR&)
            r, g, b = color[1:3], color[3:5], color[5:]
            ass_color = f"&H{b}{g}{r}&"
            color_var.set(ass_color)
            
    def get_system_fonts(self):
        """Get list of installed fonts"""
        try:
            import winreg
            import os

            # Danh sách font mặc định
            default_fonts = ["Arial", "Times New Roman", "Calibri", "Verdana", "Tahoma"]

            # Đường dẫn registry chứa font
            font_paths = [
                (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'),
                (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Fonts'),
                (winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'),
                (winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Fonts')
            ]

            installed_fonts = set()

            for hkey, path in font_paths:
                try:
                    # Mở registry key
                    key = winreg.OpenKey(hkey, path)
                    
                    # Đếm số lượng giá trị trong key
                    num_values = winreg.QueryInfoKey(key)[1]
                    
                    # Lặp qua các giá trị
                    for i in range(num_values):
                        try:
                            name, data, _ = winreg.EnumValue(key, i)
                            # Loại bỏ phần mở rộng và (TrueType)
                            clean_name = name.replace(' (TrueType)', '').replace(' (OpenType)', '').replace(' (Italic)', '')
                            installed_fonts.add(clean_name)
                        except Exception as e:
                            logging.debug(f"Error reading font registry value: {e}")
                    
                    winreg.CloseKey(key)
                except FileNotFoundError:
                    logging.debug(f"Font registry path not found: {path}")
                except PermissionError:
                    logging.debug(f"Permission denied for registry path: {path}")
                except Exception as e:
                    logging.debug(f"Error accessing font registry path {path}: {e}")

            # Thêm một số font phổ biến khác
            additional_fonts = [
                "Segoe UI", "Microsoft Sans Serif", "Consolas", 
                "Courier New", "Georgia", "Palatino Linotype"
            ]
            
            # Kết hợp font mặc định, font từ hệ thống và font bổ sung
            all_fonts = list(set(default_fonts + list(installed_fonts) + additional_fonts))
            
            return sorted(all_fonts)

        except Exception as e:
            logging.error(f"Unexpected error getting system fonts: {e}")
            return default_fonts

    def validate_color_format(self, color: str) -> bool:
        """Validate ASS color format"""
        if not color:
            return False
        if not (color.startswith('&H') and color.endswith('&')):
            return False
        # Remove &H and & from start and end
        color_value = color[2:-1]
        if len(color_value) != 6:
            return False
        try:
            # Check if it's a valid hex value
            int(color_value, 16)
            return True
        except ValueError:
            return False

    def validate_numeric_value(self, value: str, min_val: float, max_val: float, allow_float: bool = False) -> bool:
        """Validate numeric input"""
        try:
            if allow_float:
                num = float(value)
            else:
                num = int(value)
            return min_val <= num <= max_val
        except ValueError:
            return False

    def validate_font(self, font_name: str) -> bool:
        """Validate font name"""
        return font_name in self.get_system_fonts()

    def validate_inputs(self) -> tuple[bool, str]:
        """Validate all inputs before processing"""
        # Check files
        if not self.audio_path.get():
            return False, "Please select an audio file"
        if not Path(self.audio_path.get()).exists():
            return False, "Audio file does not exist"
            
        if not self.subtitle_path.get():
            return False, "Please select a subtitle file"
        if not Path(self.subtitle_path.get()).exists():
            return False, "Subtitle file does not exist"
            
        if self.overlay1_path.get() and not Path(self.overlay1_path.get()).exists():
            return False, "Overlay 1 file does not exist"
        if self.overlay2_path.get() and not Path(self.overlay2_path.get()).exists():
            return False, "Overlay 2 file does not exist"

        # Validate font settings
        if not self.validate_font(self.font_var.get()):
            return False, "Invalid font selected"
        if not self.validate_numeric_value(self.font_size_var.get(), 1, 100, False):
            return False, "Font size must be between 1 and 100"

        # Validate colors
        if not self.validate_color_format(self.primary_color_var.get()):
            return False, "Invalid primary color format"
        if not self.validate_color_format(self.outline_color_var.get()):
            return False, "Invalid outline color format"
        if not self.validate_color_format(self.back_color_var.get()):
            return False, "Invalid background color format"

        # Validate style settings
        if not self.validate_numeric_value(self.outline_width_var.get(), 0, 10, True):
            return False, "Outline width must be between 0 and 10"
        if not self.validate_numeric_value(self.shadow_width_var.get(), 0, 10, True):
            return False, "Shadow width must be between 0 and 10"

        # Validate margins
        if not self.validate_numeric_value(self.margin_v_var.get(), 0, 300, False):
            return False, "Vertical margin must be between 0 and 300"
        if not self.validate_numeric_value(self.margin_h_var.get(), 0, 300, False):
            return False, "Horizontal margin must be between 0 and 300"

        # Validate alignment and max chars
        if not self.validate_numeric_value(self.alignment_var.get(), 1, 9, False):
            return False, "Alignment must be between 1 and 9"
        if not self.validate_numeric_value(self.max_chars_var.get(), 10, 100, False):
            return False, "Max characters must be between 10 and 100"

        return True, ""

    def sanitize_color(self, color: str) -> str:
        """Ensure color is in correct ASS format"""
        # Chuyển về chữ hoa
        color = color.upper()
        
        # Đảm bảo có &H ở đầu
        if not color.startswith('&H'):
            color = '&H' + color.lstrip('&')
            
        # Đảm bảo có & ở cuối
        if not color.endswith('&'):
            color = color.rstrip('&') + '&'
            
        # Đảm bảo đúng độ dài
        color_value = color[2:-1]  # Bỏ &H và &
        if len(color_value) > 6:
            color_value = color_value[:6]
        elif len(color_value) < 6:
            color_value = color_value.zfill(6)
            
        return f"&H{color_value}&"

    def get_subtitle_config(self) -> Optional[dict]:
        """Get subtitle config from GUI with validation"""
        try:
            # Validate all inputs first
            valid, error_msg = self.validate_inputs()
            if not valid:
                messagebox.showerror("Validation Error", error_msg)
                return None

            # Log current values
            logging.debug(f"Primary color from GUI: {self.primary_color_var.get()}")
            logging.debug(f"Outline color from GUI: {self.outline_color_var.get()}")
            logging.debug(f"Back color from GUI: {self.back_color_var.get()}")

            # Sanitize and convert values
            config = {
                'font_name': self.font_var.get().strip(),
                'font_size': int(self.font_size_var.get()),
                'primary_color': self.primary_color_var.get(),
                'outline_color': self.outline_color_var.get(),
                'back_color': self.back_color_var.get(),
                'outline_width': float(self.outline_width_var.get()),
                'shadow_width': float(self.shadow_width_var.get()),
                'margin_v': int(self.margin_v_var.get()),
                'margin_h': int(self.margin_h_var.get()),
                'alignment': int(self.alignment_var.get()),
                'max_chars': int(self.max_chars_var.get())
            }

            # Log the config for debugging
            logging.debug(f"Generated subtitle config: {config}")
            return config

        except Exception as e:
            logging.error(f"Error creating subtitle config: {str(e)}")
            messagebox.showerror("Error", f"Failed to create subtitle config: {str(e)}")
            return None

    def save_settings(self):
        """Save current settings to file"""
        config = self.get_subtitle_config()
        if config:
            try:
                config_path = self.base_path / 'config'
                config_path.mkdir(exist_ok=True)
                
                with open(config_path / 'settings.json', 'w') as f:
                    json.dump(config, f, indent=4)
                    
                messagebox.showinfo("Success", "Settings saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
                
    def load_settings(self):
        """Load settings from file"""
        try:
            config_path = self.base_path / 'config' / 'settings.json'
            if config_path.exists():
                with open(config_path) as f:
                    saved_settings = json.load(f)
                self.subtitle_settings.update(saved_settings)
        except Exception as e:
            logging.error(f"Failed to load settings: {str(e)}")
            
    def process_video(self):
        """Process video with validation and error handling"""
        try:
            # Step 1: Validate inputs and get config
            config = self.get_subtitle_config()
            if not config:
                return

            # Step 2: Create necessary directories
            for dir_name in ['temp', 'final']:
                dir_path = self.base_path / dir_name
                dir_path.mkdir(exist_ok=True)

            # Step 3: Prepare paths
            audio_path = Path(self.audio_path.get())
            subtitle_path = Path(self.subtitle_path.get())
            overlay1_path = Path(self.overlay1_path.get()) if self.overlay1_path.get() else None
            overlay2_path = Path(self.overlay2_path.get()) if self.overlay2_path.get() else None

            # Step 4: Process video with progress updates
            messagebox.showinfo("Processing", "Starting video processing...")
            
            output_path = self.video_processor.process_video(
                audio_path,
                subtitle_path,
                overlay1_path,
                overlay2_path,
                config
            )

            # Step 5: Show success message with output path
            messagebox.showinfo("Success", f"Video processed successfully!\nOutput: {output_path}")

        except Exception as e:
            error_msg = str(e)
            logging.error(f"Error in processing: {error_msg}")
            messagebox.showerror("Error", f"Failed to process video: {error_msg}")

    def init_settings_manager(self):
        """Khởi tạo settings manager và load presets"""
        self.settings_manager = SettingsManager(Path(os.getcwd()))
        self.update_preset_list()
        
    def update_preset_list(self):
        """Cập nhật danh sách preset trong combobox"""
        preset_names = self.settings_manager.get_preset_names()
        self.preset_combo['values'] = preset_names
        
    def save_preset(self):
        """Lưu settings hiện tại thành preset mới"""
        name = self.new_preset_var.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a preset name")
            return
            
        settings = {
            'font_name': self.font_var.get(),
            'font_size': self.font_size_var.get(),
            'primary_color': self.primary_color_var.get(),
            'outline_color': self.outline_color_var.get(),
            'back_color': self.back_color_var.get(),
            'margin_h': self.margin_h_var.get(),
            'max_chars': self.max_chars_var.get()
            # Thêm các settings khác tùy theo nhu cầu
        }
        
        if self.settings_manager.save_preset(name, settings):
            messagebox.showinfo("Success", f"Preset '{name}' saved successfully")
            self.update_preset_list()
            self.new_preset_var.set("")  # Clear entry
        else:
            messagebox.showerror("Error", f"Failed to save preset '{name}'")
            
    def load_selected_preset(self, event=None):
        """Load preset đã chọn"""
        name = self.preset_var.get()
        if not name:
            return
            
        settings = self.settings_manager.load_preset(name)
        if settings:
            # Áp dụng settings vào GUI
            self.font_var.set(settings.get('font_name', 'Arial'))
            self.font_size_var.set(settings.get('font_size', 20))
            self.primary_color_var.set(settings.get('primary_color', '&HFFFFFF&'))
            self.outline_color_var.set(settings.get('outline_color', '&H000000&'))
            self.back_color_var.set(settings.get('back_color', '&H000000&'))
            self.margin_h_var.set(settings.get('margin_h', 100))
            self.max_chars_var.set(settings.get('max_chars', 40))
            # Áp dụng các settings khác
            
            messagebox.showinfo("Success", f"Preset '{name}' loaded successfully")
        else:
            messagebox.showerror("Error", f"Failed to load preset '{name}'")
            
    def delete_preset(self):
        """Xóa preset đã chọn"""
        name = self.preset_var.get()
        if not name:
            messagebox.showwarning("Warning", "Please select a preset to delete")
            return
            
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete preset '{name}'?"):
            if self.settings_manager.delete_preset(name):
                messagebox.showinfo("Success", f"Preset '{name}' deleted successfully")
                self.preset_var.set("")  # Clear selection
                self.update_preset_list()
            else:
                messagebox.showerror("Error", f"Failed to delete preset '{name}'")

    def refresh_video_counts(self):
        """Refresh video counts in raw and cut directories"""
        try:
            raw_videos = self.file_manager.get_raw_videos()
            cut_videos = self.file_manager.get_cut_videos()
            
            self.raw_count_label.config(text=f"{len(raw_videos)} videos")
            self.cut_count_label.config(text=f"{len(cut_videos)} videos")
        except Exception as e:
            logging.error(f"Error refreshing video counts: {e}")
            messagebox.showerror("Error", f"Failed to refresh video counts: {str(e)}")
    
    def process_raw_videos(self):
        """Process raw videos into cut segments"""
        try:
            # Get settings
            min_duration = float(self.min_duration_var.get())
            max_duration = float(self.max_duration_var.get())
            
            # Validate settings
            if min_duration <= 0 or max_duration <= 0 or min_duration >= max_duration:
                raise ValueError("Invalid duration settings")
            
            # Process videos
            segments = self.video_cutter.process_raw_videos(
                min_duration=min_duration,
                max_duration=max_duration
            )
            
            # Refresh counts
            self.refresh_video_counts()
            
            # Show success message
            messagebox.showinfo("Success", 
                              f"Successfully created {len(segments)} video segments!")
            
        except Exception as e:
            logging.error(f"Error processing raw videos: {e}")
            messagebox.showerror("Error", f"Failed to process raw videos: {str(e)}")

class SettingsManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.presets_path = path_manager.get_preset_path("")  # Get presets directory
        self.presets_path.parent.mkdir(exist_ok=True)
        
    def get_preset_names(self):
        """Get list of preset names"""
        try:
            preset_files = list(self.presets_path.parent.glob("*.json"))
            return [preset.stem for preset in preset_files]
        except Exception as e:
            logging.error(f"Error getting preset names: {e}")
            return []
            
    def save_preset(self, name, settings):
        """Save preset to file"""
        try:
            preset_path = self.presets_path.parent / f"{name}.json"
            with open(preset_path, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving preset: {e}")
            
    def load_preset(self, name):
        """Load preset from file"""
        try:
            preset_path = self.presets_path.parent / f"{name}.json"
            if preset_path.exists():
                with open(preset_path) as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading preset: {e}")
        return None
        
    def delete_preset(self, name):
        """Delete preset file"""
        try:
            preset_path = self.presets_path.parent / f"{name}.json"
            if preset_path.exists():
                preset_path.unlink()
        except Exception as e:
            logging.error(f"Error deleting preset: {e}")

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(level=logging.DEBUG,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    root = tk.Tk()
    app = VideoMakerGUI(root)
    root.mainloop()
