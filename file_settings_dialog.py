"""
File Settings Dialog for Faster Whisper GUI.
Allows editing settings for a single file in the queue.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QCheckBox, QGroupBox, QScrollArea, QWidget,
    QRadioButton, QButtonGroup, QSpinBox, QDoubleSpinBox, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QWheelEvent


class NoWheelComboBox(QComboBox):
    """QComboBox that ignores wheel events to prevent accidental scrolling."""
    def wheelEvent(self, event: QWheelEvent):
        """Ignore wheel events to prevent accidental value changes."""
        event.ignore()  # Don't process the wheel event

from presets import get_preset, get_preset_names
from help_texts import get_tooltip, get_detailed_help


class HelpButton(QPushButton):
    """Small help button for dialogs."""
    def __init__(self, help_key, parent=None):
        super().__init__("?", parent)
        self.setMaximumWidth(30)
        self.setToolTip("Click for detailed help")
        self.help_key = help_key
        self.clicked.connect(self.show_help)
    
    def show_help(self):
        """Show help dialog."""
        from gui_main import HelpDialog
        help_info = get_detailed_help(self.help_key)
        dialog = HelpDialog(help_info["title"], help_info["content"], self.parent())
        dialog.exec()


class FileSettingsDialog(QDialog):
    """Dialog for editing settings for a single file."""
    
    def __init__(self, file_path, initial_options, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.options = initial_options.copy()
        self.init_ui()
        self.load_options()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle(f"Edit Settings - {Path(self.file_path).name}")
        self.setMinimumWidth(800)
        self.setMinimumHeight(700)
        
        layout = QVBoxLayout()
        
        # File info
        file_label = QLabel(f"File: {Path(self.file_path).name}")
        file_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(file_label)
        
        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_widget.setLayout(scroll_layout)
        
        # Presets
        preset_group = QGroupBox("Preset")
        preset_layout = QHBoxLayout()
        self.preset_group = QButtonGroup()
        for preset_name in get_preset_names():
            radio = QRadioButton(preset_name)
            self.preset_group.addButton(radio)
            preset_layout.addWidget(radio)
        preset_layout.addStretch()
        preset_group.setLayout(preset_layout)
        scroll_layout.addWidget(preset_group)
        
        # Basic Options
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
        task_layout.addWidget(HelpButton("task", self))
        basic_layout.addLayout(task_layout)
        
        # Model
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = NoWheelComboBox()
        self.model_combo.addItems([
            "large-v3", "large-v3-turbo", "large-v2", "large-v1",
            "medium", "small", "base", "tiny"
        ])
        model_layout.addWidget(self.model_combo, 1)
        model_layout.addWidget(HelpButton("model", self))
        basic_layout.addLayout(model_layout)
        
        # Language
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
        lang_layout.addWidget(self.language_combo, 1)
        lang_layout.addWidget(HelpButton("language", self))
        basic_layout.addLayout(lang_layout)
        
        # Translate to Language (only shown when Translate is selected)
        self.translate_to_layout = QHBoxLayout()
        self.translate_to_label = QLabel("Translate to:")
        self.translate_to_combo = NoWheelComboBox()
        self.translate_to_combo.addItem("English", "en")
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
        format_layout.addWidget(HelpButton("output_formats", self))
        basic_layout.addLayout(format_layout)
        
        basic_group.setLayout(basic_layout)
        scroll_layout.addWidget(basic_group)
        
        # Speaker Diarization
        self.diarize_group = QGroupBox("Speaker Diarization")
        diarize_layout = QVBoxLayout()
        
        # Enable diarization
        diarize_enable_layout = QHBoxLayout()
        self.diarize_enable = QCheckBox("Enable Speaker Diarization")
        self.diarize_enable.stateChanged.connect(self.toggle_diarization_options)
        diarize_enable_layout.addWidget(self.diarize_enable)
        diarize_enable_layout.addStretch()
        diarize_enable_layout.addWidget(HelpButton("diarize_enable", self))
        diarize_layout.addLayout(diarize_enable_layout)
        
        # Diarization method
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Diarization Method:"))
        self.diarize_method_combo = NoWheelComboBox()
        self.diarize_method_combo.addItems(["pyannote_v3.1", "pyannote_v3.0", "reverb_v2", "reverb_v1"])
        method_layout.addWidget(self.diarize_method_combo, 1)
        method_layout.addWidget(HelpButton("diarize_method", self))
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
        speaker_count_layout.addStretch()
        speaker_count_layout.addWidget(HelpButton("diarization_settings", self))
        diarize_layout.addLayout(speaker_count_layout)
        
        # Speaker label
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("Speaker Label:"))
        self.speaker_label_edit = QLineEdit("SPEAKER")
        label_layout.addWidget(self.speaker_label_edit, 1)
        label_layout.addWidget(HelpButton("speaker_label", self))
        diarize_layout.addLayout(label_layout)
        
        # Diarization device
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Diarization Device:"))
        self.diarize_device_combo = NoWheelComboBox()
        self.diarize_device_combo.addItems(["auto", "cuda", "cpu"])
        device_layout.addWidget(self.diarize_device_combo, 1)
        device_layout.addWidget(HelpButton("diarize_device", self))
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
        threads_layout.addWidget(HelpButton("diarize_threads", self))
        diarize_layout.addLayout(threads_layout)
        
        # Advanced diarization options
        self.advanced_diarize_group = QGroupBox("Advanced Diarization Options")
        advanced_diarize_layout = QVBoxLayout()
        
        # Diarize Only
        diarize_only_layout = QHBoxLayout()
        self.diarize_only_check = QCheckBox("Diarize Only (no transcription)")
        diarize_only_layout.addWidget(self.diarize_only_check)
        diarize_only_layout.addStretch()
        diarize_only_layout.addWidget(HelpButton("diarize_only", self))
        advanced_diarize_layout.addLayout(diarize_only_layout)
        
        # Return Embeddings
        embeddings_layout = QHBoxLayout()
        self.return_embeddings_check = QCheckBox("Return Embeddings")
        embeddings_layout.addWidget(self.return_embeddings_check)
        embeddings_layout.addStretch()
        embeddings_layout.addWidget(HelpButton("return_embeddings", self))
        advanced_diarize_layout.addLayout(embeddings_layout)
        
        # Diarize After Filters
        diarize_ff_layout = QHBoxLayout()
        diarize_ff_layout.addWidget(QLabel("Diarize After Filters:"))
        self.diarize_ff_check = QCheckBox()
        self.diarize_ff_check.setChecked(True)
        diarize_ff_layout.addWidget(self.diarize_ff_check)
        diarize_ff_layout.addStretch()
        diarize_ff_layout.addWidget(HelpButton("diarize_ff", self))
        advanced_diarize_layout.addLayout(diarize_ff_layout)
        
        # Dump Diarization Output
        dump_layout = QHBoxLayout()
        self.diarize_dump_check = QCheckBox("Dump Diarization Output")
        dump_layout.addWidget(self.diarize_dump_check)
        dump_layout.addStretch()
        dump_layout.addWidget(HelpButton("diarize_dump", self))
        advanced_diarize_layout.addLayout(dump_layout)
        
        self.advanced_diarize_group.setLayout(advanced_diarize_layout)
        self.advanced_diarize_group.setCheckable(True)
        self.advanced_diarize_group.setChecked(False)
        diarize_layout.addWidget(self.advanced_diarize_group)
        
        self.diarize_group.setLayout(diarize_layout)
        scroll_layout.addWidget(self.diarize_group)
        
        # Initially disable diarization options
        self.toggle_diarization_options(0)
        
        # Common Options
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
        vad_layout.addWidget(HelpButton("vad_enable", self))
        common_layout.addLayout(vad_layout)
        
        vad_method_layout = QHBoxLayout()
        vad_method_layout.addWidget(QLabel("VAD Method:"))
        self.vad_method_combo = NoWheelComboBox()
        self.vad_method_combo.addItems(["silero_v4_fw", "silero_v5_fw", "pyannote_v3", "webrtc", "auditok"])
        vad_method_layout.addWidget(self.vad_method_combo, 1)
        vad_method_layout.addWidget(HelpButton("vad_method", self))
        common_layout.addLayout(vad_method_layout)
        
        # Word timestamps
        word_ts_layout = QHBoxLayout()
        self.word_timestamps_check = QCheckBox("Word Timestamps")
        self.word_timestamps_check.setChecked(True)
        word_ts_layout.addWidget(self.word_timestamps_check)
        word_ts_layout.addStretch()
        word_ts_layout.addWidget(HelpButton("word_timestamps", self))
        common_layout.addLayout(word_ts_layout)
        
        # Highlight words
        highlight_layout = QHBoxLayout()
        self.highlight_words_check = QCheckBox("Highlight Words (Karaoke)")
        highlight_layout.addWidget(self.highlight_words_check)
        highlight_layout.addStretch()
        highlight_layout.addWidget(HelpButton("highlight_words", self))
        common_layout.addLayout(highlight_layout)
        
        self.common_group.setLayout(common_layout)
        scroll_layout.addWidget(self.common_group)
        
        # Audio Filters
        self.filters_group = QGroupBox("Audio Filters")
        self.filters_group.setCheckable(True)
        self.filters_group.setChecked(False)
        filters_layout = QVBoxLayout()
        
        # Speech Normalization
        speechnorm_layout = QHBoxLayout()
        self.ff_speechnorm_check = QCheckBox("Speech Normalization")
        speechnorm_layout.addWidget(self.ff_speechnorm_check)
        speechnorm_layout.addStretch()
        speechnorm_layout.addWidget(HelpButton("ff_speechnorm", self))
        filters_layout.addLayout(speechnorm_layout)
        
        # Loudness Normalization
        loudnorm_layout = QHBoxLayout()
        self.ff_loudnorm_check = QCheckBox("Loudness Normalization")
        loudnorm_layout.addWidget(self.ff_loudnorm_check)
        loudnorm_layout.addStretch()
        loudnorm_layout.addWidget(HelpButton("ff_loudnorm", self))
        filters_layout.addLayout(loudnorm_layout)
        
        # Low/High Pass Filter
        lowhighpass_layout = QHBoxLayout()
        self.ff_lowhighpass_check = QCheckBox("Low/High Pass Filter")
        lowhighpass_layout.addWidget(self.ff_lowhighpass_check)
        lowhighpass_layout.addStretch()
        lowhighpass_layout.addWidget(HelpButton("ff_lowhighpass", self))
        filters_layout.addLayout(lowhighpass_layout)
        
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
        tempo_layout.addWidget(HelpButton("ff_tempo", self))
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
        denoise_layout.addWidget(HelpButton("ff_fftdn", self))
        filters_layout.addLayout(denoise_layout)
        
        self.filters_group.setLayout(filters_layout)
        scroll_layout.addWidget(self.filters_group)
        
        # Advanced Options
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
        temp_layout.addWidget(HelpButton("temperature", self))
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
        beam_layout.addWidget(HelpButton("beam_size", self))
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
        patience_layout.addWidget(HelpButton("patience", self))
        advanced_layout.addLayout(patience_layout)
        
        # Device
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Device:"))
        self.device_combo = NoWheelComboBox()
        self.device_combo.addItems(["auto", "cuda", "cpu"])
        device_layout.addWidget(self.device_combo, 1)
        device_layout.addWidget(HelpButton("device_selection", self))
        advanced_layout.addLayout(device_layout)
        
        # Compute type
        compute_layout = QHBoxLayout()
        compute_layout.addWidget(QLabel("Compute Type:"))
        self.compute_type_combo = NoWheelComboBox()
        self.compute_type_combo.addItems(["auto", "default", "int8", "float16", "float32"])
        compute_layout.addWidget(self.compute_type_combo, 1)
        compute_layout.addWidget(HelpButton("compute_type", self))
        advanced_layout.addLayout(compute_layout)
        
        # Standard presets
        standard_layout = QHBoxLayout()
        standard_preset_layout = QHBoxLayout()
        self.standard_check = QCheckBox("Standard Preset")
        standard_preset_layout.addWidget(self.standard_check)
        standard_preset_layout.addStretch()
        standard_preset_layout.addWidget(HelpButton("standard_preset", self))
        standard_layout.addLayout(standard_preset_layout)
        
        standard_asia_layout = QHBoxLayout()
        self.standard_asia_check = QCheckBox("Standard Asia Preset")
        standard_asia_layout.addWidget(self.standard_asia_check)
        standard_asia_layout.addStretch()
        standard_asia_layout.addWidget(HelpButton("standard_asia_preset", self))
        standard_layout.addLayout(standard_asia_layout)
        standard_layout.addStretch()
        advanced_layout.addLayout(standard_layout)
        
        # Batch options
        batch_layout = QHBoxLayout()
        batch_recursive_layout = QHBoxLayout()
        self.batch_recursive_check = QCheckBox("Batch Recursive")
        batch_recursive_layout.addWidget(self.batch_recursive_check)
        batch_recursive_layout.addStretch()
        batch_recursive_layout.addWidget(HelpButton("batch_recursive", self))
        batch_layout.addLayout(batch_recursive_layout)
        
        check_files_layout = QHBoxLayout()
        self.check_files_check = QCheckBox("Check Files")
        check_files_layout.addWidget(self.check_files_check)
        check_files_layout.addStretch()
        check_files_layout.addWidget(HelpButton("check_files", self))
        batch_layout.addLayout(check_files_layout)
        batch_layout.addStretch()
        advanced_layout.addLayout(batch_layout)
        
        self.advanced_group.setLayout(advanced_layout)
        scroll_layout.addWidget(self.advanced_group)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px;")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
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
    
    def load_options(self):
        """Load options into the UI."""
        # Task
        if self.options.get("task") == "translate":
            self.task_translate.setChecked(True)
        else:
            self.task_transcribe.setChecked(True)
        self.on_task_changed()
        
        # Model
        model = self.options.get("model", "large-v2")
        index = self.model_combo.findText(model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        
        # Language
        lang = self.options.get("language", "auto")
        if lang == "auto" or lang == "None":
            self.language_combo.setCurrentIndex(0)
        else:
            index = self.language_combo.findData(lang)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)
            else:
                index = self.language_combo.findText(lang)
                if index >= 0:
                    self.language_combo.setCurrentIndex(index)
        
        # Output formats
        formats = self.options.get("output_formats", ["srt"])
        self.format_srt.setChecked("srt" in formats or "all" in formats)
        self.format_vtt.setChecked("vtt" in formats or "all" in formats)
        self.format_txt.setChecked("txt" in formats or "text" in formats or "all" in formats)
        self.format_json.setChecked("json" in formats or "all" in formats)
        
        # VAD
        self.vad_enable_check.setChecked(self.options.get("vad_enable", True))
        vad_method = self.options.get("vad_method", "silero_v4_fw")
        index = self.vad_method_combo.findText(vad_method)
        if index >= 0:
            self.vad_method_combo.setCurrentIndex(index)
        
        # Word timestamps
        self.word_timestamps_check.setChecked(self.options.get("word_timestamps", True))
        self.highlight_words_check.setChecked(self.options.get("highlight_words", False))
        
        # Diarization
        diarize_enabled = self.options.get("diarize_enable", False)
        self.diarize_enable.setChecked(diarize_enabled)
        if diarize_enabled:
            diarize_method = self.options.get("diarize_method", "pyannote_v3.1")
            index = self.diarize_method_combo.findText(diarize_method)
            if index >= 0:
                self.diarize_method_combo.setCurrentIndex(index)
            
            num = self.options.get("num_speakers", 0)
            self.num_speakers_spin.setValue(num)
            min_sp = self.options.get("min_speakers", 0)
            self.min_speakers_spin.setValue(min_sp)
            max_sp = self.options.get("max_speakers", 0)
            self.max_speakers_spin.setValue(max_sp)
            
            speaker_label = self.options.get("speaker_label", "SPEAKER")
            self.speaker_label_edit.setText(speaker_label)
            
            diarize_device = self.options.get("diarize_device", "auto")
            index = self.diarize_device_combo.findText(diarize_device)
            if index >= 0:
                self.diarize_device_combo.setCurrentIndex(index)
            
            threads = self.options.get("diarize_threads", 0)
            self.diarize_threads_spin.setValue(threads)
            
            self.diarize_only_check.setChecked(self.options.get("diarize_only", False))
            self.return_embeddings_check.setChecked(self.options.get("return_embeddings", False))
            self.diarize_ff_check.setChecked(self.options.get("diarize_ff", True))
            self.diarize_dump_check.setChecked(self.options.get("diarize_dump", False))
        
        # Audio filters
        self.ff_speechnorm_check.setChecked(self.options.get("ff_speechnorm", False))
        self.ff_loudnorm_check.setChecked(self.options.get("ff_loudnorm", False))
        self.ff_lowhighpass_check.setChecked(self.options.get("ff_lowhighpass", False))
        tempo = self.options.get("ff_tempo", 1.0)
        self.ff_tempo_spin.setValue(tempo)
        denoise = self.options.get("ff_fftdn", 0)
        self.ff_fftdn_spin.setValue(denoise)
        
        # Advanced
        self.temperature_spin.setValue(self.options.get("temperature", 0.0))
        self.beam_size_spin.setValue(self.options.get("beam_size", 5))
        self.patience_spin.setValue(self.options.get("patience", 2.0))
        
        device = self.options.get("device", "auto")
        index = self.device_combo.findText(device)
        if index >= 0:
            self.device_combo.setCurrentIndex(index)
        
        compute_type = self.options.get("compute_type", "auto")
        index = self.compute_type_combo.findText(compute_type)
        if index >= 0:
            self.compute_type_combo.setCurrentIndex(index)
        
        self.standard_check.setChecked(self.options.get("standard", False))
        self.standard_asia_check.setChecked(self.options.get("standard_asia", False))
        self.batch_recursive_check.setChecked(self.options.get("batch_recursive", False))
        self.check_files_check.setChecked(self.options.get("check_files", False))
    
    def get_options(self):
        """Get current options from UI."""
        options = {}
        
        # Task
        options["task"] = "translate" if self.task_translate.isChecked() else "transcribe"
        
        # Model
        options["model"] = self.model_combo.currentText()
        
        # Language
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
        
        # Word timestamps
        options["word_timestamps"] = self.word_timestamps_check.isChecked()
        options["highlight_words"] = self.highlight_words_check.isChecked()
        
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
            speaker_label = self.speaker_label_edit.text()
            if speaker_label:
                options["speaker_label"] = speaker_label
            options["diarize_device"] = self.diarize_device_combo.currentText()
            threads = self.diarize_threads_spin.value()
            if threads > 0:
                options["diarize_threads"] = threads
            options["diarize_only"] = self.diarize_only_check.isChecked()
            options["return_embeddings"] = self.return_embeddings_check.isChecked()
            options["diarize_ff"] = self.diarize_ff_check.isChecked()
            options["diarize_dump"] = self.diarize_dump_check.isChecked()
            # Sentence mode (auto-enabled with diarization)
            options["sentence"] = True
        
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
        options["standard_asia"] = self.standard_asia_check.isChecked()
        options["batch_recursive"] = self.batch_recursive_check.isChecked()
        options["check_files"] = self.check_files_check.isChecked()
        options["print_progress"] = True  # Always show progress
        
        return options
