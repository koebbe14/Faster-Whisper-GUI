"""
Main GUI application for Faster Whisper.
Provides a user-friendly interface for faster-whisper-xxl.exe
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox, QSpinBox,
    QDoubleSpinBox, QGroupBox, QTextEdit, QFileDialog, QMessageBox,
    QDialog, QScrollArea, QRadioButton, QButtonGroup, QSlider,
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QThread, QTimer, QMimeData, QEvent
from PyQt6.QtGui import QIcon, QFont, QKeySequence, QShortcut, QDragEnterEvent, QDropEvent, QWheelEvent


class NoWheelComboBox(QComboBox):
    """QComboBox that ignores wheel events to prevent accidental scrolling."""
    def wheelEvent(self, event: QWheelEvent):
        """Ignore wheel events to prevent accidental value changes."""
        event.ignore()  # Don't process the wheel event

from command_builder import build_command, validate_options
from process_manager import ProcessManager
from presets import get_preset, get_preset_names
from help_texts import get_tooltip, get_detailed_help
from command_preview_dialog import CommandPreviewDialog
from file_info_extractor import get_file_info
from processing_queue import ProcessingQueue, JobStatus, QueueJob
from model_checker import get_all_model_statuses, get_model_download_info, get_model_info_display
from speaker_replacement_dialog import SpeakerReplacementDialog
from timestamp_removal_dialog import TimestampRemovalDialog
from queue_settings_dialog import QueueSettingsDialog
from queue_window import QueueWindow
from audio_analyzer import analyze_audio_quality


def check_gpu_available():
    """Check if GPU/CUDA is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        # Try alternative method if torch not available
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=2)
            return result.returncode == 0
        except:
            return False


def get_gpu_info():
    """Get GPU information if available."""
    try:
        import torch
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0) if device_count > 0 else "Unknown"
            return {
                "available": True,
                "count": device_count,
                "name": device_name
            }
    except ImportError:
        pass
    return {"available": False, "count": 0, "name": None}


class BestPracticesDialog(QDialog):
    """Dialog showing best practices for maximum accuracy."""
    
    def __init__(self, parent=None, show_diarization_tips=False):
        super().__init__(parent)
        self.setWindowTitle("Best Practices for Maximum Accuracy")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Tips for Maximum Transcription & Speaker Recognition Accuracy")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # Content
        content_text = QTextEdit()
        content_text.setReadOnly(True)
        
        tips = """For Maximum Transcription Accuracy:

✓ Set exact speaker count when using diarization
  • Set "Number of Speakers" to the exact count
  • This is the SINGLE MOST IMPORTANT setting for speaker recognition accuracy

✓ Specify language explicitly (don't use auto-detect)
  • Auto-detect can reduce accuracy, especially for interviews
  • Select the exact language spoken in your audio

✓ Use large-v2 model for best results
  • More accurate than smaller models
  • Fewer hallucinations than v3 models

✓ Enable GPU if available for faster processing
  • GPU allows using maximum accuracy settings (beam_size=10, patience=5.0)
  • Much faster than CPU (5-10x speedup)

✓ Use minimal audio filters for clean recordings
  • iPhone recordings in quiet environments are typically high quality
  • Aggressive denoising can actually REDUCE accuracy for clean audio
  • Only use loudness normalization for clean recordings

✓ Enable Word Timestamps
  • Required for accurate timestamps
  • Improves overall transcription quality"""
        
        if show_diarization_tips:
            tips += """


⚠️ DIARIZATION-SPECIFIC TIPS:

• Set exact speaker count - This dramatically improves accuracy
• Use pyannote_v3.1 method (latest and most accurate)
• Enable "Diarize After Filters" for better results when using audio filters"""
        
        content_text.setPlainText(tips)
        layout.addWidget(content_text)
        
        # Don't show again checkbox
        self.dont_show_checkbox = QCheckBox("Don't show this dialog again")
        layout.addWidget(self.dont_show_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("Got it!")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def should_show_again(self):
        """Check if user wants to see this dialog again."""
        return not self.dont_show_checkbox.isChecked()


class HelpDialog(QDialog):
    """Dialog for displaying detailed help information."""
    
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout()
        
        # Content text
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(content)
        text_edit.setFont(QFont("Arial", 10))
        layout.addWidget(text_edit)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


class AboutDialog(QDialog):
    """Dialog for displaying application information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Faster Whisper GUI")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Faster Whisper GUI")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # Version
        version_label = QLabel("Version 1.0")
        version_label.setStyleSheet("font-size: 10pt; color: #666; padding: 5px;")
        layout.addWidget(version_label)
        
        # Description
        desc_text = QTextEdit()
        desc_text.setReadOnly(True)
        desc_text.setPlainText(
            "A user-friendly graphical interface for faster-whisper-xxl.exe\n\n"
            "This application provides an easy-to-use GUI for transcribing and translating "
            "audio and video files using the Faster Whisper model.\n\n"
            "Features:\n"
            "• Support for multiple audio/video formats\n"
            "• Speaker diarization (identify different speakers)\n"
            "• Multiple output formats (SRT, VTT, TXT, JSON)\n"
            "• Batch processing with customizable settings per file\n"
            "• Audio filters for improved quality\n"
            "• Real-time progress tracking\n\n"
            "Based on faster-whisper-xxl.exe by Purfview\n"
            "GitHub: https://github.com/Purfview/whisper-standalone-win"
        )
        desc_text.setFont(QFont("Arial", 10))
        layout.addWidget(desc_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


class HelpMenuDialog(QDialog):
    """Dialog for displaying general help information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help - Faster Whisper GUI")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Faster Whisper GUI - Help")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # Help content
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        
        # Build help text as a single string
        help_content = """Faster Whisper GUI - User Guide
==================================================

GETTING STARTED
--------------------------------------------------
1. Select Files: Click 'Select Files/Folder...' or drag and drop files/folders
2. Choose Output Folder: Leave empty to save in source folder, or browse to select
3. Configure Settings: Use presets or customize options
4. Start Processing: Click 'Start Processing' button

PRESETS
--------------------------------------------------
• Standard: Balanced settings for general use
• Turbo: Optimized for speed
• Diarize: Optimized for speaker diarization accuracy

Note: Presets provide starting configurations. You can modify any settings after selecting a preset.

BASIC OPTIONS
--------------------------------------------------
• Task: Choose Transcribe (keep original language) or Translate (to English)
• Model: Select the Whisper model (larger = more accurate but slower)
• Language: Select the language spoken in the audio, or use Auto-detect
• Output Formats: Choose SRT, VTT, TXT, and/or JSON subtitle formats

SPEAKER DIARIZATION
--------------------------------------------------
Enable this feature to identify different speakers in your audio.
• Method: Choose the diarization algorithm (pyannote_v3.1 recommended)
• Number of Speakers: Set if you know the exact count, or leave on Auto
• Min/Max Speakers: Set a range if you're unsure of the exact count
• Speaker Label: Customize the prefix used for speaker labels (default: SPEAKER)

After processing with diarization enabled, a "Speaker Identification & Replacement" dialog will automatically open. This allows you to:
• Review the full diarized transcript
• See all identified speakers (SPEAKER_00, SPEAKER_01, etc.) in a table
• Replace generic speaker labels with actual names (e.g., "John", "Sarah")
• Preview changes before saving
• Save the updated transcript to a new file with custom speaker names

You can also access this feature later by clicking the "Identify & Replace Speakers" button that appears after processing.

COMMON OPTIONS
--------------------------------------------------
• VAD (Voice Activity Detection): Filters out non-speech segments
• Word Timestamps: Include precise timing for each word
• Highlight Words: Create karaoke-style subtitles with word-level highlighting

AUDIO FILTERS
--------------------------------------------------
Improve audio quality before processing:
• Speech Normalization: Normalize speech levels
• Loudness Normalization: Standardize audio loudness
• Low/High Pass Filter: Remove unwanted frequencies
• Tempo: Adjust playback speed (1.0 = normal)
• Denoise: Reduce background noise (0 = disabled)

ADVANCED OPTIONS
--------------------------------------------------
• Temperature: Controls randomness (0.0 = deterministic)
• Beam Size: Number of beams for beam search (higher = more accurate, slower)
• Patience: Early stopping patience
• Device: Choose auto, CUDA (GPU), or CPU
• Compute Type: Model quantization type

MULTIPLE FILES
--------------------------------------------------
When processing multiple files:
1. Select multiple files or a folder
2. Configure your settings
3. Click 'Start Processing'
4. In the Queue Settings dialog, choose to apply same or different settings to each file
5. Review and edit settings for individual files if needed
6. The Processing Queue window will show progress for all files

TIPS
--------------------------------------------------
• Use the '?' buttons next to options for detailed explanations
• For best diarization accuracy, use large-v2 model with higher beam_size (more reliable than v3 models)
• Enable 'Diarize After Filters' for better accuracy when using audio filters
• Check Model Status from the File menu to see which models are available
• Keyboard shortcuts: Ctrl+O (open files), Ctrl+S (start), Ctrl+C (cancel), F1 (help)

NEED MORE HELP?
--------------------------------------------------
Click the '?' buttons throughout the interface for detailed help on specific options.
For technical documentation, visit: https://github.com/Purfview/whisper-standalone-win"""
        
        help_text.setPlainText(help_content)
        help_text.setFont(QFont("Arial", 10))
        layout.addWidget(help_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


class FasterWhisperGUI(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.input_files = []
        self.output_dir = ""
        self.process_manager = ProcessManager()
        self.queue = ProcessingQueue()
        self.processing_start_time = None
        self.current_file_index = 0
        self.total_files = 0
        self.last_output_dir = None
        self.output_files_generated = []
        self.queue_window = None
        self.current_queue_file_index = 0
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        self.init_ui()
        self.setup_keyboard_shortcuts()
        self.setup_validation()
        self.load_defaults()
        # Update reminders after loading defaults
        self.update_reminders()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Faster Whisper GUI")
        self.setMinimumSize(900, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        # 1. File Selection Section
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel(
            "You can select multiple files or a folder containing files. "
            "Multiple files will be processed in a queue with the option to use the same or different settings for each file."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 5px; background-color: #f9f9f9; border-radius: 3px;")
        file_layout.addWidget(info_label)
        
        # Input files
        input_layout = QHBoxLayout()
        self.input_files_label = QLabel("No files selected (drag & drop files or folders here)")
        self.input_files_label.setStyleSheet("padding: 10px; border: 2px dashed #ccc; border-radius: 5px;")
        input_btn = QPushButton("Select Files/Folder...")
        input_btn.clicked.connect(self.select_input_files)
        input_layout.addWidget(self.input_files_label, 1)
        input_layout.addWidget(input_btn)
        
        # Audio analysis button (optional, independent)
        self.analyze_audio_btn = QPushButton("Analyze Audio Quality")
        self.analyze_audio_btn.setToolTip("Analyze selected audio files and get suggestions for optimal settings")
        self.analyze_audio_btn.setEnabled(False)  # Disabled until files are selected
        self.analyze_audio_btn.clicked.connect(self.analyze_audio_quality)
        input_layout.addWidget(self.analyze_audio_btn)
        
        file_layout.addLayout(input_layout)
        
        # File info display
        self.file_info_label = QLabel("")
        self.file_info_label.setWordWrap(True)
        self.file_info_label.setStyleSheet("color: #666; font-size: 9pt; padding: 5px;")
        self.file_info_label.setVisible(False)
        file_layout.addWidget(self.file_info_label)
        
        # Output folder
        output_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Output folder (leave empty for source folder)")
        output_btn = QPushButton("Browse...")
        output_btn.clicked.connect(self.select_output_folder)
        output_layout.addWidget(QLabel("Output Folder:"))
        output_layout.addWidget(self.output_dir_edit, 1)
        output_layout.addWidget(output_btn)
        file_layout.addLayout(output_layout)
        
        file_group.setLayout(file_layout)
        scroll_layout.addWidget(file_group)
        
        # 2. Presets Panel
        preset_group = QGroupBox("Presets")
        preset_layout = QVBoxLayout()
        
        # Preset buttons with help button
        preset_header_layout = QHBoxLayout()
        preset_buttons_layout = QHBoxLayout()
        self.preset_group = QButtonGroup()
        for preset_name in get_preset_names():
            # Add explanation for Diarize preset
            button_text = preset_name
            if preset_name == "Diarize":
                button_text = "Diarize (label speakers)"
            radio = QRadioButton(button_text)
            self.preset_group.addButton(radio)
            preset_buttons_layout.addWidget(radio)
            if preset_name == "Standard":
                radio.setChecked(True)
        self.preset_group.buttonClicked.connect(self.apply_preset)
        preset_buttons_layout.addStretch()
        preset_header_layout.addLayout(preset_buttons_layout)
        self.add_help_button(preset_header_layout, "presets")
        preset_layout.addLayout(preset_header_layout)
        
        # Preset info label
        self.preset_info_label = QLabel("Presets provide starting configurations. You can modify any settings after selecting a preset.")
        self.preset_info_label.setWordWrap(True)
        self.preset_info_label.setStyleSheet("color: #666; font-style: italic;")
        preset_layout.addWidget(self.preset_info_label)
        
        preset_group.setLayout(preset_layout)
        scroll_layout.addWidget(preset_group)
        
        # 2. Basic Options
        basic_group = QGroupBox("Basic Options")
        basic_layout = QVBoxLayout()
        
        # Task
        task_layout = QHBoxLayout()
        task_layout.addWidget(QLabel("Task:"))
        self.task_transcribe = QRadioButton("Transcribe")
        self.task_translate = QRadioButton("Translate")
        self.task_transcribe.setChecked(True)
        self.task_transcribe.toggled.connect(self.on_task_changed)
        self.task_translate.toggled.connect(self.on_task_changed)
        task_layout.addWidget(self.task_transcribe)
        task_layout.addWidget(self.task_translate)
        task_layout.addStretch()
        self.add_help_button(task_layout, "task")
        basic_layout.addLayout(task_layout)
        
        # Model
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = NoWheelComboBox()
        # Add models in order of accuracy (best to fastest)
        self.model_combo.addItems([
            "large-v3",           # Latest full model (best accuracy)
            "large-v3-turbo",     # Latest turbo model (fast + accurate)
            "large-v2",           # Previous generation (excellent accuracy)
            "large-v1",           # Older large model
            "medium",             # Balanced option
            "small",              # Smaller, faster
            "base",               # Base model
            "tiny"                # Smallest, fastest
        ])
        model_layout.addWidget(self.model_combo, 1)
        self.add_help_button(model_layout, "model")
        basic_layout.addLayout(model_layout)
        
        # Source Language (language spoken in audio)
        lang_layout = QHBoxLayout()
        self.source_lang_label = QLabel("Language:")
        lang_layout.addWidget(self.source_lang_label)
        self.language_combo = NoWheelComboBox()
        self.language_combo.addItem("Auto-detect", "auto")
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Spanish", "es")
        self.language_combo.addItem("French", "fr")
        self.language_combo.addItem("German", "de")
        self.language_combo.addItem("Japanese", "ja")
        self.language_combo.addItem("Chinese", "zh")
        self.language_combo.addItem("Italian", "it")
        self.language_combo.addItem("Portuguese", "pt")
        self.language_combo.addItem("Russian", "ru")
        self.language_combo.addItem("Korean", "ko")
        self.language_combo.addItem("Arabic", "ar")
        self.language_combo.addItem("Hindi", "hi")
        # Add more languages as needed
        lang_layout.addWidget(self.language_combo, 1)
        self.add_help_button(lang_layout, "language")
        basic_layout.addLayout(lang_layout)
        
        # Language reminder label
        self.language_reminder_label = QLabel("💡 Tip: For best accuracy, specify the language explicitly (don't use auto-detect)")
        self.language_reminder_label.setWordWrap(True)
        self.language_reminder_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        self.language_reminder_label.setVisible(False)  # Hidden by default
        basic_layout.addWidget(self.language_reminder_label)
        
        # Translate to Language (only shown when Translate is selected)
        self.translate_to_layout = QHBoxLayout()
        self.translate_to_label = QLabel("Translate to:")
        self.translate_to_combo = NoWheelComboBox()
        self.translate_to_combo.addItem("English", "en")
        # Note: Faster Whisper only translates to English, but we show this for clarity
        self.translate_to_combo.setEnabled(False)  # Always English in faster-whisper
        self.translate_to_layout.addWidget(self.translate_to_label)
        self.translate_to_layout.addWidget(self.translate_to_combo, 1)
        self.translate_to_layout.addStretch()
        self.translate_to_label.setVisible(False)
        self.translate_to_combo.setVisible(False)
        basic_layout.addLayout(self.translate_to_layout)
        
        # Output formats
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Output Formats:"))
        self.format_srt = QCheckBox("SRT")
        self.format_vtt = QCheckBox("VTT")
        self.format_txt = QCheckBox("TXT")
        self.format_json = QCheckBox("JSON")
        self.format_srt.setChecked(True)
        format_layout.addWidget(self.format_srt)
        format_layout.addWidget(self.format_vtt)
        format_layout.addWidget(self.format_txt)
        format_layout.addWidget(self.format_json)
        format_layout.addStretch()
        self.add_help_button(format_layout, "output_formats")
        basic_layout.addLayout(format_layout)
        
        basic_group.setLayout(basic_layout)
        scroll_layout.addWidget(basic_group)
        
        # 4. Speaker Diarization (PROMINENT SECTION)
        self.diarize_group = QGroupBox("Speaker Diarization")
        diarize_layout = QVBoxLayout()
        
        # Enable diarization
        diarize_enable_layout = QHBoxLayout()
        self.diarize_enable = QCheckBox("Enable Speaker Diarization")
        self.diarize_enable.stateChanged.connect(self.toggle_diarization_options)
        diarize_enable_layout.addWidget(self.diarize_enable)
        diarize_enable_layout.addStretch()
        self.add_help_button(diarize_enable_layout, "diarize_enable")
        diarize_layout.addLayout(diarize_enable_layout)
        
        # Diarization method
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Diarization Method:"))
        self.diarize_method_combo = NoWheelComboBox()
        self.diarize_method_combo.addItems(["pyannote_v3.1", "pyannote_v3.0", "reverb_v2", "reverb_v1"])
        method_layout.addWidget(self.diarize_method_combo, 1)
        self.add_help_button(method_layout, "diarize_method")
        diarize_layout.addLayout(method_layout)
        
        # Speaker count settings
        speaker_count_layout = QHBoxLayout()
        speaker_count_layout.addWidget(QLabel("Number of Speakers:"))
        self.num_speakers_spin = QSpinBox()
        self.num_speakers_spin.setMinimum(0)
        self.num_speakers_spin.setMaximum(100)
        self.num_speakers_spin.setSpecialValueText("Auto")
        self.num_speakers_spin.setValue(0)
        speaker_count_layout.addWidget(self.num_speakers_spin)
        speaker_count_layout.addWidget(QLabel("Min:"))
        self.min_speakers_spin = QSpinBox()
        self.min_speakers_spin.setMinimum(0)
        self.min_speakers_spin.setMaximum(100)
        self.min_speakers_spin.setSpecialValueText("None")
        self.min_speakers_spin.setValue(0)
        speaker_count_layout.addWidget(self.min_speakers_spin)
        speaker_count_layout.addWidget(QLabel("Max:"))
        self.max_speakers_spin = QSpinBox()
        self.max_speakers_spin.setMinimum(0)
        self.max_speakers_spin.setMaximum(100)
        self.max_speakers_spin.setSpecialValueText("None")
        self.max_speakers_spin.setValue(0)
        speaker_count_layout.addWidget(self.max_speakers_spin)
        speaker_count_layout.addStretch()
        self.add_help_button(speaker_count_layout, "diarization_settings")
        diarize_layout.addLayout(speaker_count_layout)
        
        # Speaker count reminder label
        self.speaker_count_reminder_label = QLabel("⚠️ Tip: Setting the exact number of speakers dramatically improves accuracy.")
        self.speaker_count_reminder_label.setWordWrap(True)
        self.speaker_count_reminder_label.setStyleSheet("color: #d97706; font-style: italic; padding: 5px; background-color: #fef3c7; border-radius: 3px;")
        self.speaker_count_reminder_label.setVisible(False)  # Hidden by default
        diarize_layout.addWidget(self.speaker_count_reminder_label)
        
        # Speaker label
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("Speaker Label:"))
        self.speaker_label_edit = QLineEdit("SPEAKER")
        label_layout.addWidget(self.speaker_label_edit, 1)
        self.add_help_button(label_layout, "speaker_label")
        diarize_layout.addLayout(label_layout)
        
        # Diarization device
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Diarization Device:"))
        self.diarize_device_combo = NoWheelComboBox()
        self.diarize_device_combo.addItems(["auto", "cuda", "cpu"])
        device_layout.addWidget(self.diarize_device_combo, 1)
        self.add_help_button(device_layout, "diarize_device")
        diarize_layout.addLayout(device_layout)
        
        # Diarization threads
        threads_layout = QHBoxLayout()
        threads_layout.addWidget(QLabel("Diarization Threads:"))
        self.diarize_threads_spin = QSpinBox()
        self.diarize_threads_spin.setMinimum(0)
        self.diarize_threads_spin.setMaximum(32)
        self.diarize_threads_spin.setSpecialValueText("Auto")
        self.diarize_threads_spin.setValue(0)
        threads_layout.addWidget(self.diarize_threads_spin)
        threads_layout.addStretch()
        self.add_help_button(threads_layout, "diarize_threads")
        diarize_layout.addLayout(threads_layout)
        
        # Advanced diarization options (collapsible)
        self.advanced_diarize_group = QGroupBox("Advanced Diarization Options")
        advanced_diarize_layout = QVBoxLayout()
        
        # Diarize Only
        diarize_only_layout = QHBoxLayout()
        self.diarize_only_check = QCheckBox("Diarize Only (no transcription)")
        diarize_only_layout.addWidget(self.diarize_only_check)
        diarize_only_layout.addStretch()
        self.add_help_button(diarize_only_layout, "diarize_only")
        advanced_diarize_layout.addLayout(diarize_only_layout)
        
        # Return Embeddings
        embeddings_layout = QHBoxLayout()
        self.return_embeddings_check = QCheckBox("Return Embeddings")
        embeddings_layout.addWidget(self.return_embeddings_check)
        embeddings_layout.addStretch()
        self.add_help_button(embeddings_layout, "return_embeddings")
        advanced_diarize_layout.addLayout(embeddings_layout)
        
        # Diarize After Filters
        diarize_ff_layout = QHBoxLayout()
        diarize_ff_layout.addWidget(QLabel("Diarize After Filters:"))
        self.diarize_ff_check = QCheckBox()
        self.diarize_ff_check.setChecked(True)
        diarize_ff_layout.addWidget(self.diarize_ff_check)
        diarize_ff_layout.addStretch()
        self.add_help_button(diarize_ff_layout, "diarize_ff")
        advanced_diarize_layout.addLayout(diarize_ff_layout)
        
        # Dump Diarization Output
        dump_layout = QHBoxLayout()
        self.diarize_dump_check = QCheckBox("Dump Diarization Output")
        dump_layout.addWidget(self.diarize_dump_check)
        dump_layout.addStretch()
        self.add_help_button(dump_layout, "diarize_dump")
        advanced_diarize_layout.addLayout(dump_layout)
        
        self.advanced_diarize_group.setLayout(advanced_diarize_layout)
        self.advanced_diarize_group.setCheckable(True)
        self.advanced_diarize_group.setChecked(False)
        diarize_layout.addWidget(self.advanced_diarize_group)
        
        self.diarize_group.setLayout(diarize_layout)
        scroll_layout.addWidget(self.diarize_group)
        
        # Initially disable diarization options
        self.toggle_diarization_options(0)
        
        # 5. Common Options (collapsible)
        self.common_group = QGroupBox("Common Options")
        self.common_group.setCheckable(True)
        self.common_group.setChecked(False)
        common_layout = QVBoxLayout()
        
        # VAD
        vad_layout = QHBoxLayout()
        self.vad_enable_check = QCheckBox("Enable VAD (Voice Activity Detection)")
        self.vad_enable_check.setChecked(True)
        vad_layout.addWidget(self.vad_enable_check)
        vad_layout.addStretch()
        self.add_help_button(vad_layout, "vad_enable")
        common_layout.addLayout(vad_layout)
        
        vad_method_layout = QHBoxLayout()
        vad_method_layout.addWidget(QLabel("VAD Method:"))
        self.vad_method_combo = NoWheelComboBox()
        self.vad_method_combo.addItems(["silero_v4_fw", "silero_v5_fw", "pyannote_v3", "webrtc", "auditok"])
        vad_method_layout.addWidget(self.vad_method_combo, 1)
        self.add_help_button(vad_method_layout, "vad_method")
        common_layout.addLayout(vad_method_layout)
        
        # Word timestamps
        word_ts_layout = QHBoxLayout()
        self.word_timestamps_check = QCheckBox("Word Timestamps")
        self.word_timestamps_check.setChecked(True)
        # Connect to validation to handle standard preset requirement
        self.word_timestamps_check.toggled.connect(self.on_word_timestamps_toggled)
        word_ts_layout.addWidget(self.word_timestamps_check)
        word_ts_layout.addStretch()
        self.add_help_button(word_ts_layout, "word_timestamps")
        common_layout.addLayout(word_ts_layout)
        
        # Highlight words
        highlight_layout = QHBoxLayout()
        self.highlight_words_check = QCheckBox("Highlight Words (Karaoke)")
        highlight_layout.addWidget(self.highlight_words_check)
        highlight_layout.addStretch()
        self.add_help_button(highlight_layout, "highlight_words")
        common_layout.addLayout(highlight_layout)
        
        self.common_group.setLayout(common_layout)
        scroll_layout.addWidget(self.common_group)
        
        # 6. Audio Filters (collapsible)
        self.filters_group = QGroupBox("Audio Filters")
        self.filters_group.setCheckable(True)
        self.filters_group.setChecked(False)
        filters_layout = QVBoxLayout()
        
        # Speech Normalization
        speechnorm_layout = QHBoxLayout()
        self.ff_speechnorm_check = QCheckBox("Speech Normalization")
        speechnorm_layout.addWidget(self.ff_speechnorm_check)
        speechnorm_layout.addStretch()
        self.add_help_button(speechnorm_layout, "ff_speechnorm")
        filters_layout.addLayout(speechnorm_layout)
        self.add_tooltip(self.ff_speechnorm_check, "ff_speechnorm")
        
        # Loudness Normalization
        loudnorm_layout = QHBoxLayout()
        self.ff_loudnorm_check = QCheckBox("Loudness Normalization")
        loudnorm_layout.addWidget(self.ff_loudnorm_check)
        loudnorm_layout.addStretch()
        self.add_help_button(loudnorm_layout, "ff_loudnorm")
        filters_layout.addLayout(loudnorm_layout)
        self.add_tooltip(self.ff_loudnorm_check, "ff_loudnorm")
        
        # Low/High Pass Filter
        lowhighpass_layout = QHBoxLayout()
        self.ff_lowhighpass_check = QCheckBox("Low/High Pass Filter")
        lowhighpass_layout.addWidget(self.ff_lowhighpass_check)
        lowhighpass_layout.addStretch()
        self.add_help_button(lowhighpass_layout, "ff_lowhighpass")
        filters_layout.addLayout(lowhighpass_layout)
        self.add_tooltip(self.ff_lowhighpass_check, "ff_lowhighpass")
        
        # Tempo
        tempo_layout = QHBoxLayout()
        tempo_layout.addWidget(QLabel("Tempo:"))
        self.ff_tempo_spin = QDoubleSpinBox()
        self.ff_tempo_spin.setMinimum(0.5)
        self.ff_tempo_spin.setMaximum(2.0)
        self.ff_tempo_spin.setSingleStep(0.1)
        self.ff_tempo_spin.setValue(1.0)
        self.ff_tempo_spin.setDecimals(1)
        tempo_layout.addWidget(self.ff_tempo_spin)
        tempo_layout.addWidget(QLabel("(1.0 = normal speed)"))
        tempo_layout.addStretch()
        self.add_help_button(tempo_layout, "ff_tempo")
        filters_layout.addLayout(tempo_layout)
        
        # Denoise
        denoise_layout = QHBoxLayout()
        denoise_layout.addWidget(QLabel("Denoise:"))
        self.ff_fftdn_spin = QSpinBox()
        self.ff_fftdn_spin.setMinimum(0)
        self.ff_fftdn_spin.setMaximum(97)
        self.ff_fftdn_spin.setValue(0)
        self.ff_fftdn_spin.setSpecialValueText("Disabled")
        denoise_layout.addWidget(self.ff_fftdn_spin)
        denoise_layout.addStretch()
        self.add_help_button(denoise_layout, "ff_fftdn")
        filters_layout.addLayout(denoise_layout)
        
        self.filters_group.setLayout(filters_layout)
        scroll_layout.addWidget(self.filters_group)
        
        # 7. Advanced Options (collapsible)
        self.advanced_group = QGroupBox("Advanced Options")
        self.advanced_group.setCheckable(True)
        self.advanced_group.setChecked(False)
        advanced_layout = QVBoxLayout()
        
        # Temperature
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setMinimum(0.0)
        self.temperature_spin.setMaximum(1.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(0.0)
        self.temperature_spin.setDecimals(1)
        temp_layout.addWidget(self.temperature_spin)
        temp_layout.addStretch()
        self.add_help_button(temp_layout, "temperature")
        advanced_layout.addLayout(temp_layout)
        
        # Beam size
        beam_layout = QHBoxLayout()
        beam_layout.addWidget(QLabel("Beam Size:"))
        self.beam_size_spin = QSpinBox()
        self.beam_size_spin.setMinimum(1)
        self.beam_size_spin.setMaximum(10)
        self.beam_size_spin.setValue(5)
        beam_layout.addWidget(self.beam_size_spin)
        beam_layout.addStretch()
        self.add_help_button(beam_layout, "beam_size")
        advanced_layout.addLayout(beam_layout)
        
        # Patience
        patience_layout = QHBoxLayout()
        patience_layout.addWidget(QLabel("Patience:"))
        self.patience_spin = QDoubleSpinBox()
        self.patience_spin.setMinimum(0.0)
        self.patience_spin.setMaximum(10.0)
        self.patience_spin.setSingleStep(0.1)
        self.patience_spin.setValue(2.0)
        self.patience_spin.setDecimals(1)
        patience_layout.addWidget(self.patience_spin)
        patience_layout.addStretch()
        self.add_help_button(patience_layout, "patience")
        advanced_layout.addLayout(patience_layout)
        
        # Device
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Device:"))
        self.device_combo = NoWheelComboBox()
        self.device_combo.addItems(["auto", "cuda", "cpu"])
        device_layout.addWidget(self.device_combo, 1)
        self.add_help_button(device_layout, "device_selection")
        advanced_layout.addLayout(device_layout)
        
        # GPU detection message
        self.gpu_info_label = QLabel()
        self.gpu_info_label.setWordWrap(True)
        self.gpu_info_label.setStyleSheet("color: #059669; font-style: italic; padding: 5px; background-color: #d1fae5; border-radius: 3px;")
        self.gpu_info_label.setVisible(False)  # Will be set based on GPU detection
        advanced_layout.addWidget(self.gpu_info_label)
        
        # Compute type
        compute_layout = QHBoxLayout()
        compute_layout.addWidget(QLabel("Compute Type:"))
        self.compute_type_combo = NoWheelComboBox()
        self.compute_type_combo.addItems(["auto", "default", "int8", "float16", "float32"])
        compute_layout.addWidget(self.compute_type_combo, 1)
        self.add_help_button(compute_layout, "compute_type")
        advanced_layout.addLayout(compute_layout)
        
        # Subtitle Formatting Options (independent of Standard Preset)
        subtitle_group = QGroupBox("Subtitle Formatting Options")
        subtitle_group.setCheckable(False)
        subtitle_layout = QVBoxLayout()
        
        # Max line width
        max_width_layout = QHBoxLayout()
        max_width_layout.addWidget(QLabel("Max Line Width:"))
        self.max_line_width_spin = QSpinBox()
        self.max_line_width_spin.setMinimum(1)
        self.max_line_width_spin.setMaximum(200)
        self.max_line_width_spin.setValue(70)  # Option 1 default (better sentence breaks)
        self.max_line_width_spin.setSpecialValueText("Auto")
        max_width_layout.addWidget(self.max_line_width_spin)
        max_width_layout.addStretch()
        self.add_help_button(max_width_layout, "max_line_width")
        subtitle_layout.addLayout(max_width_layout)
        
        # Max line count
        max_count_layout = QHBoxLayout()
        max_count_layout.addWidget(QLabel("Max Line Count:"))
        self.max_line_count_spin = QSpinBox()
        self.max_line_count_spin.setMinimum(1)
        self.max_line_count_spin.setMaximum(10)
        self.max_line_count_spin.setValue(3)  # Option 1 default (better sentence breaks)
        max_count_layout.addWidget(self.max_line_count_spin)
        max_count_layout.addStretch()
        self.add_help_button(max_count_layout, "max_line_count")
        subtitle_layout.addLayout(max_count_layout)
        
        # Max comma percentage
        max_comma_layout = QHBoxLayout()
        max_comma_layout.addWidget(QLabel("Max Comma Percentage:"))
        self.max_comma_combo = NoWheelComboBox()
        self.max_comma_combo.addItems(["20", "30", "40", "50", "60", "70", "80", "90", "100"])
        self.max_comma_combo.setCurrentText("90")  # Option 1 default (better sentence breaks)
        max_comma_layout.addWidget(self.max_comma_combo, 1)
        self.add_help_button(max_comma_layout, "max_comma_percentage")
        subtitle_layout.addLayout(max_comma_layout)
        
        # Sentence mode
        sentence_layout = QHBoxLayout()
        self.sentence_check = QCheckBox("Sentence Mode")
        self.sentence_check.setChecked(True)  # Enabled by default for better sentence segmentation
        sentence_layout.addWidget(self.sentence_check)
        sentence_layout.addStretch()
        self.add_help_button(sentence_layout, "sentence_mode")
        subtitle_layout.addLayout(sentence_layout)
        
        subtitle_group.setLayout(subtitle_layout)
        advanced_layout.addWidget(subtitle_group)
        
        # Standard presets
        standard_layout = QHBoxLayout()
        standard_preset_layout = QHBoxLayout()
        self.standard_check = QCheckBox("Standard Preset")
        standard_preset_layout.addWidget(self.standard_check)
        standard_preset_layout.addStretch()
        self.add_help_button(standard_preset_layout, "standard_preset")
        standard_layout.addLayout(standard_preset_layout)
        
        standard_layout.addStretch()
        advanced_layout.addLayout(standard_layout)
        
        # Batch options
        batch_layout = QHBoxLayout()
        batch_recursive_layout = QHBoxLayout()
        self.batch_recursive_check = QCheckBox("Batch Recursive")
        batch_recursive_layout.addWidget(self.batch_recursive_check)
        batch_recursive_layout.addStretch()
        self.add_help_button(batch_recursive_layout, "batch_recursive")
        batch_layout.addLayout(batch_recursive_layout)
        
        check_files_layout = QHBoxLayout()
        self.check_files_check = QCheckBox("Check Files")
        check_files_layout.addWidget(self.check_files_check)
        check_files_layout.addStretch()
        self.add_help_button(check_files_layout, "check_files")
        batch_layout.addLayout(check_files_layout)
        batch_layout.addStretch()
        advanced_layout.addLayout(batch_layout)
        
        self.advanced_group.setLayout(advanced_layout)
        scroll_layout.addWidget(self.advanced_group)
        
        # 8. Action Buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.start_btn.clicked.connect(self.start_processing)
        button_layout.addWidget(self.start_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_processing)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Processing Queue Window (shown when processing multiple files)
        # This will be created as a separate window/dialog when needed
        
        # 10. Output/Progress Area
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        
        # Progress bar
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.time_remaining_label = QLabel("")
        self.time_remaining_label.setVisible(False)
        progress_layout.addWidget(self.time_remaining_label)
        
        self.current_file_label = QLabel("")
        self.current_file_label.setVisible(False)
        progress_layout.addWidget(self.current_file_label)
        
        output_layout.addLayout(progress_layout)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 9))
        output_layout.addWidget(self.output_text)
        
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.open_output_btn = QPushButton("Open Output Folder")
        self.open_output_btn.setVisible(False)
        self.open_output_btn.clicked.connect(self.open_output_folder)
        status_layout.addWidget(self.open_output_btn)
        
        self.speaker_replace_btn = QPushButton("Identify & Replace Speakers")
        self.speaker_replace_btn.setVisible(False)
        self.speaker_replace_btn.clicked.connect(self.open_speaker_replacement)
        status_layout.addWidget(self.speaker_replace_btn)
        
        self.remove_timestamps_btn = QPushButton("Remove Timestamps")
        self.remove_timestamps_btn.setVisible(False)
        self.remove_timestamps_btn.clicked.connect(self.open_timestamp_removal)
        status_layout.addWidget(self.remove_timestamps_btn)
        
        output_layout.addLayout(status_layout)
        
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # Add tooltips to all relevant widgets
        self.add_all_tooltips()
    
    def create_menu_bar(self):
        """Create the menu bar with File menu."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Help menu item
        help_action = file_menu.addAction("Help")
        help_action.triggered.connect(self.show_help_menu)
        help_action.setShortcut(QKeySequence("F1"))
        
        # About menu item
        about_action = file_menu.addAction("About")
        about_action.triggered.connect(self.show_about_dialog)
        
        # Separator
        file_menu.addSeparator()
        
        # Model Status menu item
        model_status_action = file_menu.addAction("Model Status")
        model_status_action.triggered.connect(self.show_model_status_dialog)
        
        # Check for Model Updates menu item
        model_updates_action = file_menu.addAction("Check for Model Updates")
        model_updates_action.triggered.connect(self.check_model_updates)
    
    def show_help_menu(self):
        """Show the help menu dialog."""
        dialog = HelpMenuDialog(self)
        dialog.exec()
    
    def show_about_dialog(self):
        """Show the about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def show_model_status_dialog(self):
        """Show model status in a dialog."""
        from model_checker import get_model_info_display
        
        statuses = get_all_model_statuses()
        status_lines = []
        
        # Group by category for better display
        status_lines.append("⭐ Best Accuracy:")
        for model_name in ["large-v3", "large-v3-turbo", "large-v2", "large-v1"]:
            display = get_model_info_display(model_name)
            status_lines.append(f"  {model_name}: {display}")
        
        status_lines.append("\n⚖️ Balanced:")
        for model_name in ["medium"]:
            display = get_model_info_display(model_name)
            status_lines.append(f"  {model_name}: {display}")
        
        status_lines.append("\n⚡ Fast Processing:")
        for model_name in ["small", "base", "tiny"]:
            display = get_model_info_display(model_name)
            status_lines.append(f"  {model_name}: {display}")
        
        status_lines.append("\n📝 Note: Models will be downloaded automatically on first use.")
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Model Status")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Model Status")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # Status text
        status_text = QTextEdit()
        status_text.setReadOnly(True)
        status_text.setPlainText("\n".join(status_lines))
        status_text.setFont(QFont("Arial", 10))
        layout.addWidget(status_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        download_btn = QPushButton("Show Download Instructions")
        download_btn.clicked.connect(lambda: self.show_download_instructions_dialog(dialog))
        button_layout.addWidget(download_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()
    
    def show_download_instructions_dialog(self, parent_dialog=None):
        """Show download instructions for the currently selected model."""
        from model_checker import get_model_download_info
        
        current_model = self.model_combo.currentText()
        download_info = get_model_download_info(current_model)
        
        dialog = QDialog(parent_dialog or self)
        dialog.setWindowTitle(f"Download Instructions - {current_model}")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Instructions text
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        if isinstance(download_info, dict):
            text_edit.setPlainText(download_info.get('download_instructions', str(download_info)))
        else:
            text_edit.setPlainText(str(download_info))
        text_edit.setFont(QFont("Courier", 9))
        layout.addWidget(text_edit)
        
        # Link if available
        if isinstance(download_info, dict) and 'huggingface_url' in download_info:
            link_layout = QHBoxLayout()
            link_label = QLabel()
            link_label.setOpenExternalLinks(True)
            link_label.setText(f'<a href="{download_info["huggingface_url"]}">Open Model Repository in Browser</a>')
            link_layout.addWidget(link_label)
            link_layout.addStretch()
            layout.addLayout(link_layout)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def add_help_button(self, layout, help_key):
        """Add a help button to a layout."""
        help_btn = QPushButton("?")
        help_btn.setMaximumWidth(30)
        help_btn.setToolTip("Click for detailed help")
        help_btn.clicked.connect(lambda checked, key=help_key: self.show_help(key))
        layout.addWidget(help_btn)
    
    def add_tooltip(self, widget, tooltip_key):
        """Add tooltip to a widget."""
        tooltip = get_tooltip(tooltip_key)
        if tooltip:
            widget.setToolTip(tooltip)
    
    def add_all_tooltips(self):
        """Add tooltips to all relevant widgets."""
        self.add_tooltip(self.task_transcribe, "task")
        self.add_tooltip(self.task_translate, "task")
        self.add_tooltip(self.model_combo, "model")
        self.add_tooltip(self.language_combo, "language")
        self.add_tooltip(self.format_srt, "output_formats")
        self.add_tooltip(self.format_vtt, "output_formats")
        self.add_tooltip(self.format_txt, "output_formats")
        self.add_tooltip(self.format_json, "output_formats")
        self.add_tooltip(self.vad_enable_check, "vad_enable")
        self.add_tooltip(self.vad_method_combo, "vad_method")
        self.add_tooltip(self.word_timestamps_check, "word_timestamps")
        self.add_tooltip(self.highlight_words_check, "highlight_words")
        self.add_tooltip(self.diarize_enable, "diarize_enable")
        self.add_tooltip(self.diarize_method_combo, "diarize_method")
        self.add_tooltip(self.num_speakers_spin, "num_speakers")
        self.add_tooltip(self.min_speakers_spin, "min_speakers")
        self.add_tooltip(self.max_speakers_spin, "max_speakers")
        self.add_tooltip(self.speaker_label_edit, "speaker_label")
        self.add_tooltip(self.diarize_device_combo, "diarize_device")
        self.add_tooltip(self.diarize_only_check, "diarize_only")
        self.add_tooltip(self.return_embeddings_check, "return_embeddings")
        self.add_tooltip(self.diarize_ff_check, "diarize_ff")
        self.add_tooltip(self.diarize_dump_check, "diarize_dump")
    
    def show_help(self, help_key):
        """Show detailed help dialog."""
        help_info = get_detailed_help(help_key)
        dialog = HelpDialog(help_info["title"], help_info["content"], self)
        dialog.exec()
    
    def on_task_changed(self):
        """Handle task selection change."""
        is_translate = self.task_translate.isChecked()
        self.translate_to_label.setVisible(is_translate)
        self.translate_to_combo.setVisible(is_translate)
        # Update language label
        if is_translate:
            self.source_lang_label.setText("Source Language (spoken in audio):")
        else:
            self.source_lang_label.setText("Language:")
    
    def toggle_diarization_options(self, state):
        """Enable/disable diarization options based on checkbox state."""
        enabled = state == Qt.CheckState.Checked.value
        self.diarize_method_combo.setEnabled(enabled)
        self.num_speakers_spin.setEnabled(enabled)
        self.min_speakers_spin.setEnabled(enabled)
        self.max_speakers_spin.setEnabled(enabled)
        self.speaker_label_edit.setEnabled(enabled)
        self.diarize_device_combo.setEnabled(enabled)
        self.diarize_threads_spin.setEnabled(enabled)
        self.advanced_diarize_group.setEnabled(enabled)
        
        # Sentence mode is auto-enabled with diarization
        # Update sentence mode checkbox state (only if standard_check exists)
        if hasattr(self, 'standard_check') and not self.standard_check.isChecked():
            if enabled:
                # Diarization enabled: auto-enable sentence mode and disable checkbox
                self.sentence_check.setEnabled(False)
                self.sentence_check.blockSignals(True)
                self.sentence_check.setChecked(True)
                self.sentence_check.blockSignals(False)
            else:
                # Diarization disabled: allow manual control of sentence mode
                self.sentence_check.setEnabled(True)
        elif hasattr(self, 'sentence_check'):
            # If standard_check doesn't exist yet, just handle sentence mode
            if enabled:
                self.sentence_check.setEnabled(False)
                self.sentence_check.blockSignals(True)
                self.sentence_check.setChecked(True)
                self.sentence_check.blockSignals(False)
            else:
                self.sentence_check.setEnabled(True)
        
        # Trigger validation to update UI state (only if validation is set up)
        if hasattr(self, 'standard_check'):
            self.validate_settings()
    
    def select_input_files(self):
        """Open file dialog to select input files."""
        # Select multiple files directly
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio/Video Files (can select multiple)",
            "",
            "Media Files (*.mp3 *.mp4 *.wav *.m4a *.flac *.mkv *.avi *.mov *.wmv);;All Files (*.*)"
        )
        if files:
            self.input_files = files
            self.update_file_display()
    
    def select_output_folder(self):
        """Open folder dialog to select output directory."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_dir_edit.setText(folder)
    
    def apply_preset(self, button):
        """Apply preset configuration."""
        # Extract preset name (remove explanation text if present)
        preset_name = button.text()
        if " (" in preset_name:
            preset_name = preset_name.split(" (")[0]
        preset = get_preset(preset_name)
        
        if preset_name == "Custom":
            self.preset_info_label.setText("Custom mode: Configure all settings manually.")
            return  # Don't change anything for custom
        
        # Update info label
        self.preset_info_label.setText(f"'{preset_name}' preset applied. You can modify any settings - changes will override preset values.")
        
        # Apply preset values
        if "model" in preset:
            index = self.model_combo.findText(preset["model"])
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
        
        # Language
        if "language" in preset:
            lang = preset["language"]
            # Try to find by data first
            index = self.language_combo.findData(lang)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)
            else:
                # Try to find by text
                index = self.language_combo.findText(lang)
                if index >= 0:
                    self.language_combo.setCurrentIndex(index)
        
        if "vad_enable" in preset:
            self.vad_enable_check.setChecked(preset["vad_enable"])
        
        if "vad_method" in preset:
            index = self.vad_method_combo.findText(preset["vad_method"])
            if index >= 0:
                self.vad_method_combo.setCurrentIndex(index)
        
        if "standard" in preset:
            self.standard_check.setChecked(preset["standard"])
        else:
            self.standard_check.setChecked(False)
        
        # Subtitle formatting options (only apply if Standard Preset is not enabled)
        if not preset.get("standard", False):
            # Apply subtitle formatting options from preset if provided
            if "max_line_width" in preset:
                self.max_line_width_spin.setValue(preset["max_line_width"])
            else:
                # Reset to default if not in preset (Option 1 defaults)
                self.max_line_width_spin.setValue(70)
            
            if "max_line_count" in preset:
                self.max_line_count_spin.setValue(preset["max_line_count"])
            else:
                # Reset to default if not in preset (Option 1 defaults)
                self.max_line_count_spin.setValue(3)
            
            if "max_comma_cent" in preset:
                max_comma_str = str(preset["max_comma_cent"])
                index = self.max_comma_combo.findText(max_comma_str)
                if index >= 0:
                    self.max_comma_combo.setCurrentIndex(index)
            else:
                # Reset to default if not in preset (Option 1 defaults)
                self.max_comma_combo.setCurrentText("90")
            
            # Sentence mode: set from preset if provided, otherwise use default (True)
            if "sentence" in preset:
                # If diarization is enabled, sentence is auto-enabled, so we still set it but it will be overridden
                self.sentence_check.setChecked(preset["sentence"])
            elif not preset.get("diarize", False):
                # Reset to default (True) if not in preset and diarization not enabled
                self.sentence_check.setChecked(True)
        
        # Trigger validation to update UI state
        self.validate_settings()
        
        if "output_formats" in preset:
            formats = preset["output_formats"]
            self.format_srt.setChecked("srt" in formats or "all" in formats)
            self.format_vtt.setChecked("vtt" in formats or "all" in formats)
            self.format_txt.setChecked("txt" in formats or "text" in formats or "all" in formats)
            self.format_json.setChecked("json" in formats or "all" in formats)
        
        if "batch_recursive" in preset:
            self.batch_recursive_check.setChecked(preset["batch_recursive"])
        else:
            self.batch_recursive_check.setChecked(False)
        
        if "check_files" in preset:
            self.check_files_check.setChecked(preset["check_files"])
        else:
            self.check_files_check.setChecked(False)
        
        if "diarize" in preset:
            self.diarize_enable.setChecked(True)
            index = self.diarize_method_combo.findText(preset["diarize"])
            if index >= 0:
                self.diarize_method_combo.setCurrentIndex(index)
            self.toggle_diarization_options(Qt.CheckState.Checked.value)
            
            # Apply diarization-specific preset settings
            if "diarize_ff" in preset:
                self.diarize_ff_check.setChecked(preset["diarize_ff"])
        else:
            self.diarize_enable.setChecked(False)
            self.toggle_diarization_options(Qt.CheckState.Unchecked.value)
        
        # Apply audio filter settings (for all presets, not just diarization)
        if "ff_speechnorm" in preset:
            self.ff_speechnorm_check.setChecked(preset["ff_speechnorm"])
        if "ff_loudnorm" in preset:
            self.ff_loudnorm_check.setChecked(preset["ff_loudnorm"])
        if "ff_lowhighpass" in preset:
            self.ff_lowhighpass_check.setChecked(preset["ff_lowhighpass"])
        if "ff_fftdn" in preset:
            self.ff_fftdn_spin.setValue(preset["ff_fftdn"])
        
        # Apply transcription accuracy settings (for all presets)
        if "temperature" in preset:
            self.temperature_spin.setValue(preset["temperature"])
        if "beam_size" in preset:
            self.beam_size_spin.setValue(preset["beam_size"])
        if "patience" in preset:
            self.patience_spin.setValue(preset["patience"])
        if "word_timestamps" in preset:
            self.word_timestamps_check.setChecked(preset["word_timestamps"])
        
        if "output_dir" in preset:
            self.output_dir_edit.setText(preset["output_dir"])
    
    def get_options_dict(self):
        """Get all options as a dictionary."""
        options = {}
        
        # Basic options
        options["task"] = "translate" if self.task_translate.isChecked() else "transcribe"
        options["model"] = self.model_combo.currentText()
        lang_data = self.language_combo.currentData()
        options["language"] = lang_data if lang_data else self.language_combo.currentText()
        
        # Output formats
        formats = []
        if self.format_srt.isChecked():
            formats.append("srt")
        if self.format_vtt.isChecked():
            formats.append("vtt")
        if self.format_txt.isChecked():
            formats.append("txt")
        if self.format_json.isChecked():
            formats.append("json")
        options["output_formats"] = formats if formats else ["srt"]
        
        # VAD
        options["vad_enable"] = self.vad_enable_check.isChecked()
        options["vad_method"] = self.vad_method_combo.currentText()
        
        # Diarization
        options["diarize_enable"] = self.diarize_enable.isChecked()
        if options["diarize_enable"]:
            options["diarize_method"] = self.diarize_method_combo.currentText()
            num = self.num_speakers_spin.value()
            if num > 0:
                options["num_speakers"] = num
            min_sp = self.min_speakers_spin.value()
            if min_sp > 0:
                options["min_speakers"] = min_sp
            max_sp = self.max_speakers_spin.value()
            if max_sp > 0:
                options["max_speakers"] = max_sp
            options["speaker_label"] = self.speaker_label_edit.text()
            options["diarize_device"] = self.diarize_device_combo.currentText()
            threads = self.diarize_threads_spin.value()
            if threads > 0:
                options["diarize_threads"] = threads
            options["diarize_only"] = self.diarize_only_check.isChecked()
            options["return_embeddings"] = self.return_embeddings_check.isChecked()
            options["diarize_ff"] = self.diarize_ff_check.isChecked()
            options["diarize_dump"] = self.diarize_dump_check.isChecked()
        
        # Word timestamps
        options["word_timestamps"] = self.word_timestamps_check.isChecked()
        options["highlight_words"] = self.highlight_words_check.isChecked()
        
        # Sentence mode (auto-enabled with diarization OR if explicitly checked OR if Standard Preset is enabled)
        if options.get("diarize_enable") or self.sentence_check.isChecked() or self.standard_check.isChecked():
            options["sentence"] = True
        
        # Subtitle formatting options (only if Standard Preset is not enabled)
        if not self.standard_check.isChecked():
            # Max line width
            max_width = self.max_line_width_spin.value()
            if max_width > 0:  # 0 means "Auto"
                options["max_line_width"] = max_width
            
            # Max line count
            options["max_line_count"] = self.max_line_count_spin.value()
            
            # Max comma percentage
            max_comma = int(self.max_comma_combo.currentText())
            options["max_comma_cent"] = max_comma
        
        # Audio filters
        options["ff_speechnorm"] = self.ff_speechnorm_check.isChecked()
        options["ff_loudnorm"] = self.ff_loudnorm_check.isChecked()
        options["ff_lowhighpass"] = self.ff_lowhighpass_check.isChecked()
        tempo = self.ff_tempo_spin.value()
        if tempo != 1.0:
            options["ff_tempo"] = tempo
        denoise = self.ff_fftdn_spin.value()
        if denoise > 0:
            options["ff_fftdn"] = denoise
        
        # Advanced
        options["temperature"] = self.temperature_spin.value()
        options["beam_size"] = self.beam_size_spin.value()
        options["patience"] = self.patience_spin.value()
        options["device"] = self.device_combo.currentText()
        options["compute_type"] = self.compute_type_combo.currentText()
        options["standard"] = self.standard_check.isChecked()
        options["batch_recursive"] = self.batch_recursive_check.isChecked()
        options["check_files"] = self.check_files_check.isChecked()
        options["print_progress"] = True  # Always show progress
        
        return options
    
    def start_processing(self):
        """Start the transcription process."""
        if not self.input_files:
            QMessageBox.warning(self, "No Files Selected", "Please select at least one input file.")
            return
        
        # Get output directory
        output_dir = self.output_dir_edit.text().strip()
        if not output_dir:
            output_dir = "source"
        
        # Ensure output folder exists
        folder_ok, folder_msg = self.ensure_output_folder(output_dir)
        if not folder_ok:
            QMessageBox.warning(self, "Output Folder Error", folder_msg)
            return
        
        # Get options
        options = self.get_options_dict()
        
        # Validate options
        is_valid, error_msg = validate_options(options)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Options", error_msg)
            return
        
        # Run validation warnings before processing
        if not self.validate_before_processing():
            return  # User chose to cancel
        
        # Build command
        try:
            exe_path, args = build_command(self.input_files, output_dir, options)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to build command: {str(e)}")
            return
        
        # Check if single file or multiple files
        if len(self.input_files) == 1:
            # Single file - process immediately
            # Show command preview dialog
            preview_dialog = CommandPreviewDialog(exe_path, args, self)
            if preview_dialog.exec() != QDialog.DialogCode.Accepted:
                return  # User cancelled
            
            # Process immediately
            self.process_single_file(exe_path, args, output_dir)
        else:
            # Multiple files - show queue settings dialog
            # Show queue settings dialog (defaults to "same settings" mode)
            queue_dialog = QueueSettingsDialog(self.input_files, options, True, self)
            if queue_dialog.exec() != QDialog.DialogCode.Accepted:
                return  # User cancelled
            
            # Get file options from dialog
            file_options = queue_dialog.get_file_options()
            
            # Create queue window
            self.queue_window = QueueWindow(self)
            self.queue_window.setup_queue(self.input_files, file_options)
            self.queue_window.show()
            
            # Add all files to queue
            self.queue.clear_all()
            for file_path in self.input_files:
                file_opts = file_options.get(file_path, options)
                self.queue.add_job([file_path], output_dir, file_opts)
            
            # Start processing queue
            self.current_queue_file_index = 0
            self.process_next_in_queue()
    
    def process_single_file(self, exe_path, args, output_dir):
        """Process a single file immediately."""
        self.last_output_dir = output_dir
        self.output_files_generated = []
        self.processing_start_time = time.time()
        self.current_file_index = 0
        self.total_files = 1
        self.last_output_dir = output_dir
        self.output_files_generated = []
        self.processing_start_time = time.time()
        self.current_file_index = 0
        self.total_files = len(self.input_files)
        
        # Show command in output
        cmd_preview = f"{exe_path} {' '.join(args)}"
        self.output_text.append(f"Command: {cmd_preview}\n")
        self.output_text.append("-" * 80 + "\n")
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.status_label.setText("Processing...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.time_remaining_label.setVisible(True)
        self.time_remaining_label.setText("Calculating time remaining...")
        if self.total_files > 1:
            self.current_file_label.setVisible(True)
            self.current_file_label.setText(f"Processing file 1 of {self.total_files}")
        
        # Start process
        self.process_manager.start_process(
            exe_path,
            args,
            self.on_output_received,
            self.on_error_received,
            self.on_process_finished,
            self.on_error_occurred
        )
        
        # Start progress timer
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(1000)  # Update every second
    
    def on_output_received(self, line):
        """Handle output from process."""
        self.output_text.append(line)
        # Auto-scroll to bottom
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Try to extract progress information
        if "Processing file" in line or "file" in line.lower():
            # Update current file if we can parse it
            pass
    
    def on_error_received(self, line):
        """Handle error output from process."""
        self.output_text.append(f"ERROR: {line}")
    
    def on_process_finished(self, exit_code):
        """Handle process completion."""
        if hasattr(self, 'progress_timer'):
            self.progress_timer.stop()
        
        # Always try to collect output files first (even if exit_code != 0)
        # This handles cases where faster-whisper-xxl.exe completes successfully
        # but returns a non-zero exit code (e.g., Windows exception code)
        self.output_files_generated = []
        if self.last_output_dir:
            # Handle "source" output directory
            if self.last_output_dir == "source" and self.input_files:
                # Files are in the source directory (same as input file)
                source_dir = Path(self.input_files[0]).parent
                if source_dir.exists():
                    # Find generated files matching input file name pattern
                    input_stem = Path(self.input_files[0]).stem
                    for ext in ['.txt', '.srt', '.vtt', '.json']:
                        # Look for files that start with the input file name
                        pattern = f"{input_stem}*{ext}"
                        self.output_files_generated.extend(list(source_dir.glob(pattern)))
            else:
                output_path = Path(self.last_output_dir)
                if output_path.exists():
                    # Find generated files
                    for ext in ['.txt', '.srt', '.vtt', '.json']:
                        self.output_files_generated.extend(list(output_path.glob(f"*{ext}")))
        
        options = self.get_options_dict()
        
        # Treat as success if exit_code==0 OR if outputs were produced
        # This handles cases where the process completes but returns a non-zero exit code
        is_effective_success = (exit_code == 0) or (len(self.output_files_generated) > 0)
        
        if is_effective_success:
            # Show warning if exit code is non-zero but files were created
            if exit_code != 0:
                self.status_label.setText(f"Completed (with warning exit code {exit_code})")
                self.status_label.setStyleSheet("color: orange;")
            else:
                self.status_label.setText("Completed successfully!")
                self.status_label.setStyleSheet("color: green;")
            
            # Show output folder button
            self.open_output_btn.setVisible(True)
            
            # Check if diarization was used
            if options.get("diarize_enable"):
                # Show speaker replacement button
                self.speaker_replace_btn.setVisible(True)
                
                # Automatically open speaker replacement dialog
                self.open_speaker_replacement_auto()
            # Check if word timestamps were enabled and open timestamp removal dialog
            elif options.get("word_timestamps", True):
                # Show timestamp removal button
                self.remove_timestamps_btn.setVisible(True)
                
                # Automatically open timestamp removal dialog
                self.open_timestamp_removal_auto()
            else:
                # Show success message only if no special dialogs
                QMessageBox.information(
                    self,
                    "Success",
                    f"Transcription completed!\n\n"
                    f"Output folder: {self.last_output_dir}\n"
                    f"Files generated: {len(self.output_files_generated)}"
                )
            
            # Show warning popup if exit code was non-zero (but files were created)
            if exit_code != 0:
                QMessageBox.warning(
                    self, 
                    "Warning", 
                    f"Process returned exit code {exit_code}, but output files were created successfully.\n\n"
                    f"Files generated: {len(self.output_files_generated)}\n"
                    f"Output folder: {self.last_output_dir}"
                )
        elif exit_code == -1:
            self.status_label.setText("Cancelled")
        else:
            self.status_label.setText(f"Process finished with exit code {exit_code}")
            self.status_label.setStyleSheet("color: orange;")
            QMessageBox.warning(self, "Warning", f"Process finished with exit code {exit_code}")
        
        self.reset_progress_display()
    
    def on_error_occurred(self, error_msg):
        """Handle process errors."""
        self.status_label.setText(f"Error: {error_msg}")
        self.output_text.append(f"ERROR: {error_msg}\n")
        QMessageBox.critical(self, "Error", error_msg)
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
    
    def cancel_processing(self):
        """Cancel the running process."""
        self.process_manager.stop_process()
        self.status_label.setText("Cancelling...")
    
    def clear_form(self):
        """Clear the form and reset to defaults."""
        reply = QMessageBox.question(
            self,
            "Clear Form",
            "Are you sure you want to clear all settings?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.load_defaults()
            self.input_files = []
            self.input_files_label.setText("No files selected")
            self.output_text.clear()
            self.status_label.setText("Ready")
    
    def load_defaults(self):
        """Load default settings."""
        # Apply Standard preset
        for button in self.preset_group.buttons():
            if button.text() == "Standard":
                button.setChecked(True)
                self.apply_preset(button)
                break
        
        # Check GPU availability and show message
        self.check_and_show_gpu_info()
        
        # Check if best practices dialog should be shown
        self.check_best_practices_dialog()
    
    # ========== NEW FEATURE METHODS ==========
    
    def check_and_show_gpu_info(self):
        """Check GPU availability and show info message."""
        gpu_info = get_gpu_info()
        if gpu_info["available"]:
            gpu_name = gpu_info.get("name", "GPU")
            self.gpu_info_label.setText(
                f"✅ GPU detected ({gpu_name})! Using GPU will allow faster processing with maximum accuracy settings."
            )
            self.gpu_info_label.setVisible(True)
            # Auto-select CUDA if GPU is available and device is set to auto
            if self.device_combo.currentText() == "auto":
                # Device will auto-detect, but we can show the message
                pass
        else:
            self.gpu_info_label.setVisible(False)
    
    def check_best_practices_dialog(self):
        """Check if best practices dialog should be shown."""
        # Check if user has disabled the dialog
        from pathlib import Path
        import json
        
        config_file = Path.home() / ".faster_whisper_gui_config.json"
        show_dialog = True
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    show_dialog = config.get("show_best_practices", True)
            except:
                pass
        
        if show_dialog:
            dialog = BestPracticesDialog(self, show_diarization_tips=False)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if not dialog.should_show_again():
                    # Save preference
                    config_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(config_file, 'w') as f:
                        json.dump({"show_best_practices": False}, f)
    
    def analyze_audio_quality(self):
        """Analyze audio quality of selected files and show suggestions."""
        if not self.input_files:
            QMessageBox.warning(self, "No Files", "Please select audio files first.")
            return
        
        # Analyze first file (or all files)
        file_to_analyze = self.input_files[0]
        
        # Show progress
        QMessageBox.information(
            self,
            "Analyzing Audio",
            f"Analyzing audio quality of: {Path(file_to_analyze).name}\n\n"
            "This may take a moment..."
        )
        
        try:
            analysis = analyze_audio_quality(file_to_analyze)
            
            # Build message
            msg = f"Audio Quality Analysis: {Path(file_to_analyze).name}\n\n"
            msg += f"Quality Score: {analysis['quality_score']}/100\n\n"
            
            if analysis['analysis_available']:
                msg += f"Noise Level: {analysis['noise_level'].title()}\n"
                msg += f"Volume Level: {analysis['volume_level'].title()}\n\n"
            
            if analysis['suggestions']:
                msg += "Suggestions:\n"
                for suggestion in analysis['suggestions']:
                    msg += f"• {suggestion}\n"
            else:
                msg += "No specific suggestions - audio quality appears good!"
            
            QMessageBox.information(self, "Audio Quality Analysis", msg)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Analysis Failed",
                f"Could not analyze audio file:\n{str(e)}\n\n"
                "Default suggestion: Clean audio detected - using minimal filters for best accuracy"
            )
    
    def update_reminders(self):
        """Update visibility of reminder labels based on current settings."""
        # Language reminder
        lang_data = self.language_combo.currentData()
        lang_text = self.language_combo.currentText()
        if lang_data == "auto" or lang_text == "Auto-detect":
            self.language_reminder_label.setVisible(True)
        else:
            self.language_reminder_label.setVisible(False)
        
        # Speaker count reminder
        if self.diarize_enable.isChecked() and self.num_speakers_spin.value() == 0:
            self.speaker_count_reminder_label.setVisible(True)
        else:
            self.speaker_count_reminder_label.setVisible(False)
    
    def validate_before_processing(self):
        """Validate settings before processing starts and show warnings."""
        warnings = []
        info_messages = []
        
        # Check diarization settings
        if self.diarize_enable.isChecked():
            if self.num_speakers_spin.value() == 0:
                warnings.append(
                    "⚠️ Diarization is enabled but speaker count is set to Auto.\n"
                    "Setting the exact number of speakers dramatically improves accuracy."
                )
        
        # Check language
        lang_data = self.language_combo.currentData()
        lang_text = self.language_combo.currentText()
        if lang_data == "auto" or lang_text == "Auto-detect":
            info_messages.append(
                "💡 Language is set to Auto-detect.\n"
                "For best accuracy, specify the language explicitly."
            )
        
        # Check device
        device = self.device_combo.currentText()
        model = self.model_combo.currentText()
        gpu_available = check_gpu_available()
        
        if device == "cpu" and model in ["large-v2", "large-v3", "large-v3-turbo"] and gpu_available:
            warnings.append(
                "⚠️ Using CPU with large model while GPU is available.\n"
                "GPU processing is much faster (5-10x speedup).\n"
                "Consider switching Device to 'auto' or 'cuda'."
            )
        
        # Check audio filters for clean audio
        if self.filters_group.isChecked():
            if self.ff_fftdn_spin.value() > 0 or self.ff_lowhighpass_check.isChecked():
                # Check if this might be clean audio (iPhone recording)
                info_messages.append(
                    "💡 Aggressive audio filters are enabled.\n"
                    "For clean iPhone recordings in quiet environments, minimal filters (loudness normalization only) provide best accuracy."
                )
        
        # Show warnings and info messages
        if warnings:
            warning_msg = "\n\n".join(warnings)
            reply = QMessageBox.warning(
                self,
                "Settings Warning",
                warning_msg + "\n\nDo you want to continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return False
        
        if info_messages:
            info_msg = "\n\n".join(info_messages)
            QMessageBox.information(
                self,
                "Settings Information",
                info_msg
            )
        
        return True
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+O: Open files
        QShortcut(QKeySequence("Ctrl+O"), self, self.select_input_files)
        
        # Ctrl+S: Start processing
        QShortcut(QKeySequence("Ctrl+S"), self, self.start_processing)
        
        # Ctrl+C: Cancel (only when processing)
        cancel_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        cancel_shortcut.activated.connect(lambda: self.cancel_processing() if self.cancel_btn.isEnabled() else None)
        
        # F1: Help
        QShortcut(QKeySequence("F1"), self, self.show_help_menu)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.input_files_label.setStyleSheet("padding: 10px; border: 2px dashed #4CAF50; border-radius: 5px; background-color: #f0f8f0;")
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event."""
        self.input_files_label.setStyleSheet("padding: 10px; border: 2px dashed #ccc; border-radius: 5px;")
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        self.input_files_label.setStyleSheet("padding: 10px; border: 2px dashed #ccc; border-radius: 5px;")
        
        urls = [url.toLocalFile() for url in event.mimeData().urls()]
        valid_files = []
        media_extensions = {'.mp3', '.mp4', '.wav', '.m4a', '.flac', '.mkv', '.avi', '.mov', '.wmv'}
        
        for path_str in urls:
            path = Path(path_str)
            if not path.exists():
                continue
            
            if path.is_file():
                # It's a file - check if it's a media file
                if path.suffix.lower() in media_extensions:
                    valid_files.append(path_str)
            elif path.is_dir():
                # It's a folder - find all media files recursively
                folder_files = [str(f) for f in path.rglob('*') if f.suffix.lower() in media_extensions]
                valid_files.extend(folder_files)
        
        if valid_files:
            self.input_files = valid_files
            self.update_file_display()
            event.acceptProposedAction()
        else:
            QMessageBox.warning(self, "Invalid Files", "No valid media files were found in the dropped items.")
    
    def update_file_display(self):
        """Update file display and show file information."""
        from file_info_extractor import format_size
        
        if not self.input_files:
            self.input_files_label.setText("No files selected (drag & drop files or folders here)")
            self.file_info_label.setVisible(False)
            self.analyze_audio_btn.setEnabled(False)
            return
        
        # Enable analyze button when files are selected
        self.analyze_audio_btn.setEnabled(True)
        
        if len(self.input_files) == 1:
            file_path = self.input_files[0]
            self.input_files_label.setText(f"Selected: {Path(file_path).name}")
            
            # Get file info
            info = get_file_info(file_path)
            info_text = f"Size: {info['size_formatted']} | Format: {info['format']}"
            if info['duration_formatted'] != "Unknown":
                info_text += f" | Duration: {info['duration_formatted']}"
            if info['codec'] != "Unknown":
                info_text += f" | Codec: {info['codec']}"
            
            self.file_info_label.setText(info_text)
            self.file_info_label.setVisible(True)
        else:
            self.input_files_label.setText(f"Selected: {len(self.input_files)} files")
            total_size = sum(Path(f).stat().st_size for f in self.input_files if Path(f).exists())
            self.file_info_label.setText(f"Total: {len(self.input_files)} files | Total size: {format_size(total_size)}")
            self.file_info_label.setVisible(True)
    
    
    def check_model_updates(self):
        """Check for model updates and show information."""
        from model_checker import check_for_model_updates
        
        updates = check_for_model_updates()
        
        if not updates:
            QMessageBox.information(
                self,
                "Model Updates",
                "No updates detected. Models are up to date.\n\n"
                "Note: Model update checking requires internet connectivity.\n"
                "Models are typically downloaded automatically on first use."
            )
        else:
            msg = "Model updates available:\n\n"
            for model, info in updates.items():
                msg += f"{model}: {info}\n"
            QMessageBox.information(self, "Model Updates", msg)
        
        # Show download instructions for the currently selected model
        self.show_download_instructions_dialog()
    
    def setup_validation(self):
        """Setup real-time validation."""
        # Connect signals for validation
        self.standard_check.toggled.connect(self.validate_settings)
        self.diarize_enable.toggled.connect(self.validate_settings)
        
        # Connect subtitle formatting options to validation
        self.max_line_width_spin.valueChanged.connect(self.on_subtitle_option_changed)
        self.max_line_count_spin.valueChanged.connect(self.on_subtitle_option_changed)
        self.max_comma_combo.currentTextChanged.connect(self.on_subtitle_option_changed)
        self.sentence_check.toggled.connect(self.on_subtitle_option_changed)
        
        # Connect signals for reminders
        self.language_combo.currentIndexChanged.connect(self.update_reminders)
        self.diarize_enable.toggled.connect(self.update_reminders)
        self.num_speakers_spin.valueChanged.connect(self.update_reminders)
    
    def on_word_timestamps_toggled(self, checked):
        """Handle word timestamps checkbox toggle."""
        # If word_timestamps is unchecked but standard preset is enabled, show warning
        if not checked and self.standard_check.isChecked():
            QMessageBox.warning(
                self,
                "Word Timestamps Required",
                "Word Timestamps must be enabled when using Standard Preset.\n\n"
                "The Standard Preset feature requires word-level timestamps to function properly.\n\n"
                "Word Timestamps has been automatically re-enabled."
            )
            # Re-enable it
            self.word_timestamps_check.blockSignals(True)
            self.word_timestamps_check.setChecked(True)
            self.word_timestamps_check.blockSignals(False)
            self.word_timestamps_check.setToolTip("Word Timestamps is required when using Standard Preset")
        else:
            # Clear tooltip if standard is not enabled
            if not self.standard_check.isChecked():
                self.word_timestamps_check.setToolTip(get_tooltip("word_timestamps"))
    
    def on_subtitle_option_changed(self):
        """Handle changes to subtitle formatting options."""
        # If any subtitle option is changed from Standard Preset defaults, disable Standard Preset
        if self.are_subtitle_options_customized():
            if self.standard_check.isChecked():
                self.standard_check.blockSignals(True)
                self.standard_check.setChecked(False)
                self.standard_check.blockSignals(False)
                QMessageBox.information(
                    self,
                    "Standard Preset Disabled",
                    "Standard Preset has been disabled because you've customized subtitle formatting options.\n\n"
                    "Standard Preset uses fixed values for subtitle formatting. To use Standard Preset, "
                    "reset the subtitle formatting options to their default values."
                )
        self.validate_settings()
    
    def are_subtitle_options_customized(self):
        """Check if subtitle options are customized from Standard Preset defaults."""
        # Standard Preset defaults:
        # max_line_width: 42
        # max_line_count: 2
        # max_comma_percentage: 70
        # sentence: True (but we check if it's explicitly enabled, not just auto-enabled by diarization)
        
        # Check if max_line_width is not 42
        if self.max_line_width_spin.value() != 42:
            return True
        
        # Check if max_line_count is not 2
        if self.max_line_count_spin.value() != 2:
            return True
        
        # Check if max_comma_percentage is not 70
        if self.max_comma_combo.currentText() != "70":
            return True
        
        # Check if sentence mode is explicitly enabled (not just auto-enabled by diarization)
        # If diarization is enabled, sentence is auto-enabled, so we don't count that as customization
        if self.sentence_check.isChecked() and not self.diarize_enable.isChecked():
            return True
        
        return False
    
    def validate_settings(self):
        """Validate settings and show visual feedback."""
        
        # Standard preset requires word_timestamps (faster-whisper-xxl.exe requirement)
        # If standard is checked, automatically enable word_timestamps
        if self.standard_check.isChecked() and not self.word_timestamps_check.isChecked():
            self.word_timestamps_check.blockSignals(True)
            self.word_timestamps_check.setChecked(True)
            self.word_timestamps_check.blockSignals(False)
            self.word_timestamps_check.setToolTip("Word Timestamps is required when using Standard Preset")
        elif not self.standard_check.isChecked():
            # Clear the tooltip when standard is unchecked
            from help_texts import get_tooltip
            self.word_timestamps_check.setToolTip(get_tooltip("word_timestamps"))
        
        # If Standard Preset is enabled, disable subtitle formatting options and set to defaults
        if self.standard_check.isChecked():
            # Disable subtitle formatting controls
            self.max_line_width_spin.setEnabled(False)
            self.max_line_count_spin.setEnabled(False)
            self.max_comma_combo.setEnabled(False)
            self.sentence_check.setEnabled(False)
            
            # Set to Standard Preset defaults
            self.max_line_width_spin.blockSignals(True)
            self.max_line_width_spin.setValue(42)
            self.max_line_width_spin.blockSignals(False)
            
            self.max_line_count_spin.blockSignals(True)
            self.max_line_count_spin.setValue(2)
            self.max_line_count_spin.blockSignals(False)
            
            self.max_comma_combo.blockSignals(True)
            self.max_comma_combo.setCurrentText("70")
            self.max_comma_combo.blockSignals(False)
            
            # Sentence mode is enabled by Standard Preset (and also auto-enabled by diarization)
            # Always set it to True when Standard Preset is enabled
            self.sentence_check.blockSignals(True)
            self.sentence_check.setChecked(True)
            self.sentence_check.blockSignals(False)
        else:
            # Enable subtitle formatting controls (except sentence if diarization is enabled)
            self.max_line_width_spin.setEnabled(True)
            self.max_line_count_spin.setEnabled(True)
            self.max_comma_combo.setEnabled(True)
            
            # Sentence mode is always enabled if diarization is enabled, so handle that separately
            if self.diarize_enable.isChecked():
                # If diarization is enabled, sentence is auto-enabled, so disable the checkbox
                self.sentence_check.setEnabled(False)
                self.sentence_check.blockSignals(True)
                self.sentence_check.setChecked(True)
                self.sentence_check.blockSignals(False)
            else:
                # If diarization is not enabled, allow manual control of sentence mode
                self.sentence_check.setEnabled(True)
        
        # Update visual indicators
        options = self.get_options_dict()
        is_valid, error_msg = validate_options(options)
        
        if is_valid:
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setStyleSheet("color: orange;")
            if error_msg:
                self.status_label.setToolTip(error_msg)
    
    def ensure_output_folder(self, output_dir):
        """Ensure output folder exists, create if needed."""
        if not output_dir or output_dir == "source":
            return True, output_dir
        
        output_path = Path(output_dir)
        
        if output_path.exists():
            if output_path.is_dir():
                return True, output_dir
            else:
                return False, f"Path exists but is not a directory: {output_dir}"
        
        # Ask user if they want to create it
        reply = QMessageBox.question(
            self,
            "Create Folder",
            f"Output folder does not exist:\n{output_dir}\n\nCreate it now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                output_path.mkdir(parents=True, exist_ok=True)
                return True, output_dir
            except PermissionError:
                return False, f"Permission denied: Cannot create folder {output_dir}"
            except Exception as e:
                return False, f"Error creating folder: {str(e)}"
        else:
            return False, "Output folder creation cancelled"
    
    
    def process_next_in_queue(self):
        """Process the next job in the queue."""
        if not self.queue.has_pending_jobs() or self.queue.is_paused:
            if self.queue_window:
                # All done or paused
                if not self.queue.has_pending_jobs():
                    QMessageBox.information(
                        self.queue_window,
                        "Queue Complete",
                        "All files in the queue have been processed!"
                    )
            return
        
        if self.process_manager.is_running():
            return  # Already processing
        
        job = self.queue.get_next_job()
        if not job:
            return
        
        self.queue.mark_job_processing(job)
        
        # Update queue window
        if self.queue_window:
            file_path = job.input_files[0]
            file_index = self.queue_window.get_file_index(file_path)
            if file_index >= 0:
                self.queue_window.update_file_status(file_index, "Processing", "Starting...")
        
        # Process this job
        self.process_job(job)
    
    def process_job(self, job: QueueJob):
        """Process a single queue job."""
        # Build command
        try:
            exe_path, args = build_command(job.input_files, job.output_dir, job.options)
        except Exception as e:
            self.queue.mark_job_failed(job, f"Failed to build command: {str(e)}")
            if self.queue_window:
                file_path = job.input_files[0]
                file_index = self.queue_window.get_file_index(file_path)
                if file_index >= 0:
                    self.queue_window.update_file_status(file_index, "Failed", str(e))
            self.process_next_in_queue()
            return
        
        # For queue processing, skip command preview (already reviewed in queue settings)
        # Start processing directly
        self.processing_start_time = time.time()
        self.current_file_index = 0
        self.total_files = len(job.input_files)
        
        # Update main UI
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.status_label.setText(f"Processing file {self.current_queue_file_index + 1} of {len(self.input_files)}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Show command in output
        cmd_preview = f"{exe_path} {' '.join(args)}"
        self.output_text.append(f"\n{'='*80}\n")
        self.output_text.append(f"Processing: {Path(job.input_files[0]).name}\n")
        self.output_text.append(f"Command: {cmd_preview}\n")
        self.output_text.append("-" * 80 + "\n")
        
        self.process_manager.start_process(
            exe_path,
            args,
            self.on_output_received,
            self.on_error_received,
            lambda code: self.on_job_finished(job, code),
            lambda msg: self.on_job_error(job, msg)
        )
        
        # Start progress timer
        if not hasattr(self, 'progress_timer') or not self.progress_timer.isActive():
            self.progress_timer = QTimer()
            self.progress_timer.timeout.connect(self.update_progress)
            self.progress_timer.start(1000)
    
    def on_job_finished(self, job, exit_code):
        """Handle job completion."""
        file_path = job.input_files[0]
        file_index = self.queue_window.get_file_index(file_path) if self.queue_window else -1
        
        # Always try to collect output files first (even if exit_code != 0)
        # This handles cases where faster-whisper-xxl.exe completes successfully
        # but returns a non-zero exit code (e.g., Windows exception code)
        job_output_files = []
        
        # Check output directory
        output_path = Path(job.output_dir)
        if output_path.exists():
            for ext in ['.txt', '.srt', '.vtt', '.json']:
                job_output_files.extend(list(output_path.glob(f"*{ext}")))
        
        # Also check source directory if output_dir was "source"
        if not job_output_files and job.input_files:
            first_input = Path(job.input_files[0])
            if first_input.exists():
                source_dir = first_input.parent
                input_stem = first_input.stem
                for ext in ['.txt', '.srt', '.vtt', '.json']:
                    pattern = f"{input_stem}*{ext}"
                    job_output_files.extend(list(source_dir.glob(pattern)))
        
        # Treat as success if exit_code==0 OR if outputs were produced
        is_effective_success = (exit_code == 0) or (len(job_output_files) > 0)
        
        if is_effective_success:
            # Mark as completed
            if exit_code != 0:
                output_msg = f"Completed (exit code {exit_code}) - Output saved to {job.output_dir}"
            else:
                output_msg = f"Completed - Output saved to {job.output_dir}"
            
            self.queue.mark_job_completed(job)
            if file_index >= 0:
                self.queue_window.update_file_status(file_index, "Completed", output_msg)
            
            # Check if diarization was used and open speaker replacement dialog
            if job.options.get("diarize_enable") and job_output_files:
                # Use the first found file (prefer .txt, then .srt, then .vtt)
                diarization_file = None
                for ext in ['.txt', '.srt', '.vtt']:
                    for f in job_output_files:
                        if str(f).lower().endswith(ext):
                            diarization_file = f
                            break
                    if diarization_file:
                        break
                
                if diarization_file:
                    dialog = SpeakerReplacementDialog(diarization_file, self)
                    dialog.exec()
        else:
            error_msg = f"Process exited with code {exit_code}"
            self.queue.mark_job_failed(job, error_msg)
            if file_index >= 0:
                self.queue_window.update_file_status(file_index, "Failed", error_msg)
        
        self.current_queue_file_index += 1
        
        # Update main UI status
        if self.queue.has_pending_jobs():
            self.status_label.setText(f"Completed file {self.current_queue_file_index} of {len(self.input_files)}. Processing next...")
        else:
            self.status_label.setText("All files completed!")
            self.reset_progress_display()
            if self.queue_window:
                self.queue_window.update_overall_progress()
        
        # Process next job
        self.process_next_in_queue()
    
    def on_job_error(self, job, error_msg):
        """Handle job error."""
        file_path = job.input_files[0]
        file_index = self.queue_window.get_file_index(file_path) if self.queue_window else -1
        
        self.queue.mark_job_failed(job, error_msg)
        if file_index >= 0:
            self.queue_window.update_file_status(file_index, "Failed", error_msg)
        
        self.current_queue_file_index += 1
        self.process_next_in_queue()
    
    def reset_progress_display(self):
        """Reset progress display."""
        self.progress_bar.setVisible(False)
        self.time_remaining_label.setVisible(False)
        self.current_file_label.setVisible(False)
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
    
    def open_output_folder(self):
        """Open the output folder in file explorer."""
        if self.last_output_dir:
            # Handle "source" output directory
            if self.last_output_dir == "source" and self.input_files:
                # Open the source directory (same as input file)
                source_dir = Path(self.input_files[0]).parent
                if source_dir.exists():
                    import subprocess
                    import sys
                    if sys.platform == 'win32':
                        subprocess.Popen(['explorer', str(source_dir)])
                    elif sys.platform == 'darwin':
                        subprocess.Popen(['open', str(source_dir)])
                    else:
                        subprocess.Popen(['xdg-open', str(source_dir)])
                else:
                    QMessageBox.warning(self, "Folder Not Found", f"Source folder not found: {source_dir}")
            else:
                output_path = Path(self.last_output_dir)
                if output_path.exists():
                    import subprocess
                    import sys
                    if sys.platform == 'win32':
                        subprocess.Popen(['explorer', str(output_path)])
                    elif sys.platform == 'darwin':
                        subprocess.Popen(['open', str(output_path)])
                    else:
                        subprocess.Popen(['xdg-open', str(output_path)])
                else:
                    QMessageBox.warning(self, "Folder Not Found", f"Output folder not found: {self.last_output_dir}")
        else:
            QMessageBox.information(self, "No Output", "No output folder available yet.")
    
    def open_speaker_replacement(self):
        """Open speaker replacement dialog (manual trigger)."""
        self._open_speaker_replacement_dialog()
    
    def open_speaker_replacement_auto(self):
        """Automatically open speaker replacement dialog after processing."""
        # Small delay to ensure files are written
        QTimer.singleShot(500, self._open_speaker_replacement_dialog)
    
    def _open_speaker_replacement_dialog(self):
        """Internal method to open speaker replacement dialog."""
        # Try to find files in output directory
        diarization_file = None
        
        # First, check if we have collected output files
        if not self.output_files_generated and self.last_output_dir:
            output_path = Path(self.last_output_dir)
            if output_path.exists():
                for ext in ['.txt', '.srt', '.vtt']:
                    files = list(output_path.glob(f"*{ext}"))
                    if files:
                        self.output_files_generated.extend(files)
                        break
        
        # Also check source directory if output_dir was "source"
        if not self.output_files_generated and self.input_files:
            # Check the directory of the first input file
            first_input = Path(self.input_files[0])
            if first_input.exists():
                source_dir = first_input.parent
                for ext in ['.txt', '.srt', '.vtt']:
                    # Look for files with same stem as input file
                    pattern = f"{first_input.stem}*{ext}"
                    files = list(source_dir.glob(pattern))
                    if files:
                        self.output_files_generated.extend(files)
                        break
        
        # Find first diarization output file (prefer .txt, then .srt, then .vtt)
        for ext in ['.txt', '.srt', '.vtt']:
            for file_path in self.output_files_generated:
                if str(file_path).lower().endswith(ext) and file_path.exists():
                    diarization_file = file_path
                    break
            if diarization_file:
                break
        
        if not diarization_file:
            QMessageBox.warning(
                self, 
                "No Diarization Output", 
                "No diarization output files found.\n\n"
                "The speaker replacement dialog will open when you click the 'Identify & Replace Speakers' button "
                "after the output files are available."
            )
            return
        
        dialog = SpeakerReplacementDialog(diarization_file, self)
        dialog.exec()
    
    def open_timestamp_removal(self):
        """Open timestamp removal dialog (manual trigger)."""
        self._open_timestamp_removal_dialog()
    
    def open_timestamp_removal_auto(self):
        """Automatically open timestamp removal dialog after processing."""
        # Small delay to ensure files are written
        QTimer.singleShot(500, self._open_timestamp_removal_dialog)
    
    def _open_timestamp_removal_dialog(self):
        """Internal method to open timestamp removal dialog."""
        # Try to find files in output directory
        output_file = None
        
        # First, check if we have collected output files
        if hasattr(self, 'output_files_generated') and self.output_files_generated:
            # Prefer .txt files, then .srt, then .vtt
            for ext in ['.txt', '.srt', '.vtt']:
                for file_path in self.output_files_generated:
                    if str(file_path).lower().endswith(ext):
                        output_file = file_path
                        break
                if output_file:
                    break
        
        # If not found, try to find in last_output_dir
        if not output_file and hasattr(self, 'last_output_dir') and self.last_output_dir:
            output_path = Path(self.last_output_dir)
            if output_path.exists():
                # Look for output files
                for ext in ['.txt', '.srt', '.vtt']:
                    files = list(output_path.glob(f"*{ext}"))
                    if files:
                        output_file = files[0]
                        break
        
        if not output_file:
            QMessageBox.warning(
                self, 
                "No Output File", 
                "No output files found.\n\n"
                "The timestamp removal dialog will open when you click the 'Remove Timestamps' button "
                "after the output files are available."
            )
            return
        
        dialog = TimestampRemovalDialog(output_file, self)
        dialog.exec()
    
    def format_size(self, size_bytes):
        """Format file size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def update_progress(self):
        """Update progress display with time remaining."""
        if not self.processing_start_time:
            return
        
        elapsed = time.time() - self.processing_start_time
        
        # Estimate time remaining (rough estimate)
        if self.current_file_index > 0 and self.total_files > 0:
            avg_time_per_file = elapsed / self.current_file_index
            remaining_files = self.total_files - self.current_file_index
            estimated_remaining = avg_time_per_file * remaining_files
            time_str = str(timedelta(seconds=int(estimated_remaining)))
            self.time_remaining_label.setText(f"Estimated time remaining: {time_str}")
        else:
            self.time_remaining_label.setText(f"Elapsed time: {str(timedelta(seconds=int(elapsed)))}")


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern look
    
    # Check and extract runtime files before starting the application
    from runtime_extractor import ensure_runtime_files
    
    if not ensure_runtime_files():
        sys.exit(1)
    
    window = FasterWhisperGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

