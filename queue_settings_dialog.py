"""
Queue Settings Dialog for Faster Whisper GUI.
Allows users to review and edit settings for each file in a multi-file queue.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QRadioButton, QButtonGroup, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class QueueSettingsDialog(QDialog):
    """Dialog for reviewing and editing queue settings for multiple files."""
    
    def __init__(self, file_list, default_options, use_same_settings=True, parent=None):
        super().__init__(parent)
        self.file_list = file_list
        self.default_options = default_options
        self.file_options = {}  # Will store options for each file
        self.init_ui()
        # Set initial mode based on parameter
        if use_same_settings:
            self.same_settings_radio.setChecked(True)
        else:
            self.different_settings_radio.setChecked(True)
        self.apply_default_settings()
        # Call on_settings_mode_changed to set initial button states
        self.on_settings_mode_changed()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Processing Queue - Review Settings")
        self.setMinimumWidth(900)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel(
            f"Review settings for {len(self.file_list)} file(s). "
            "You can apply the same settings to all files, or customize settings for individual files."
        )
        header_label.setWordWrap(True)
        header_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(header_label)
        
        # Settings mode selection
        mode_group = QGroupBox("Settings Mode")
        mode_layout = QVBoxLayout()
        
        self.settings_mode_group = QButtonGroup()
        
        self.same_settings_radio = QRadioButton("Apply same settings to all files")
        self.same_settings_radio.setChecked(True)
        self.same_settings_radio.toggled.connect(self.on_settings_mode_changed)
        self.settings_mode_group.addButton(self.same_settings_radio)
        mode_layout.addWidget(self.same_settings_radio)
        
        self.different_settings_radio = QRadioButton("Use different settings for each file")
        self.different_settings_radio.toggled.connect(self.on_settings_mode_changed)
        self.settings_mode_group.addButton(self.different_settings_radio)
        mode_layout.addWidget(self.different_settings_radio)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # Files table
        table_label = QLabel("Files and Settings:")
        layout.addWidget(table_label)
        
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(3)
        self.files_table.setHorizontalHeaderLabels(["File", "Settings", "Actions"])
        self.files_table.horizontalHeader().setStretchLastSection(True)
        self.files_table.setAlternatingRowColors(True)
        self.files_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Populate table
        self.files_table.setRowCount(len(self.file_list))
        for i, file_path in enumerate(self.file_list):
            # File name
            file_item = QTableWidgetItem(Path(file_path).name)
            file_item.setFlags(file_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.files_table.setItem(i, 0, file_item)
            
            # Settings summary
            settings_item = QTableWidgetItem("Loading settings...")
            settings_item.setFlags(settings_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.files_table.setItem(i, 1, settings_item)
            
            # Edit button (initially disabled, will be enabled/disabled based on mode)
            edit_btn = QPushButton("Edit Settings")
            edit_btn.setEnabled(False)  # Disabled by default
            edit_btn.clicked.connect(lambda checked, idx=i: self.edit_file_settings(idx))
            self.files_table.setCellWidget(i, 2, edit_btn)
        
        self.files_table.resizeColumnsToContents()
        layout.addWidget(self.files_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        start_btn = QPushButton("Start Processing Queue")
        start_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px;")
        start_btn.clicked.connect(self.accept)
        button_layout.addWidget(start_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def apply_default_settings(self):
        """Apply default settings to all files."""
        for file_path in self.file_list:
            self.file_options[file_path] = self.default_options.copy()
        self.update_settings_display()
    
    def on_settings_mode_changed(self):
        """Handle settings mode change."""
        if self.same_settings_radio.isChecked():
            # Apply default to all
            self.apply_default_settings()
            # Disable edit buttons
            for i in range(self.files_table.rowCount()):
                btn = self.files_table.cellWidget(i, 2)
                if btn:
                    btn.setEnabled(False)
        else:
            # Enable edit buttons for individual customization
            for i in range(self.files_table.rowCount()):
                btn = self.files_table.cellWidget(i, 2)
                if btn:
                    btn.setEnabled(True)
    
    def edit_file_settings(self, file_index):
        """Open settings editor for a specific file."""
        file_path = self.file_list[file_index]
        current_options = self.file_options.get(file_path, self.default_options.copy())
        
        # Create a simplified settings editor dialog
        from file_settings_dialog import FileSettingsDialog
        dialog = FileSettingsDialog(file_path, current_options, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.file_options[file_path] = dialog.get_options()
            self.update_settings_display()
    
    def update_settings_display(self):
        """Update the settings display in the table."""
        for i, file_path in enumerate(self.file_list):
            options = self.file_options.get(file_path, self.default_options)
            
            # Create comprehensive settings summary
            summary_parts = []
            
            # Task
            task = options.get('task', 'transcribe')
            if task == 'translate':
                summary_parts.append("Translate")
            else:
                summary_parts.append("Transcribe")
            
            # Model
            model = options.get('model', 'N/A')
            summary_parts.append(f"Model: {model}")
            
            # Language
            lang = options.get('language', 'auto')
            if lang and lang != 'auto' and lang != 'None':
                summary_parts.append(f"Lang: {lang}")
            
            # Output formats
            formats = options.get('output_formats', [])
            if formats:
                format_str = ", ".join([f.upper() for f in formats if f])
                if format_str:
                    summary_parts.append(f"Formats: {format_str}")
            
            # VAD
            if options.get('vad_enable', False):
                vad_method = options.get('vad_method', '')
                if vad_method:
                    summary_parts.append(f"VAD: {vad_method}")
                else:
                    summary_parts.append("VAD: Yes")
            
            # Diarization
            if options.get('diarize_enable', False):
                diarize_method = options.get('diarize_method', '')
                if diarize_method:
                    summary_parts.append(f"Diarize: {diarize_method}")
                else:
                    summary_parts.append("Diarize: Yes")
            
            # Word timestamps
            if options.get('word_timestamps', False):
                summary_parts.append("Word TS")
            
            # Audio filters
            filter_parts = []
            if options.get('ff_speechnorm', False):
                filter_parts.append("SpeechNorm")
            if options.get('ff_loudnorm', False):
                filter_parts.append("LoudNorm")
            if options.get('ff_lowhighpass', False):
                filter_parts.append("Filter")
            if options.get('ff_tempo', 1.0) != 1.0:
                filter_parts.append(f"Tempo:{options.get('ff_tempo', 1.0)}")
            if options.get('ff_fftdn', 0) > 0:
                filter_parts.append(f"Denoise:{options.get('ff_fftdn')}")
            if filter_parts:
                summary_parts.append(f"Filters: {', '.join(filter_parts)}")
            
            # Advanced options (if non-default)
            if options.get('beam_size', 5) != 5:
                summary_parts.append(f"Beam:{options.get('beam_size')}")
            if options.get('temperature', 0.0) != 0.0:
                summary_parts.append(f"Temp:{options.get('temperature')}")
            
            summary = " | ".join(summary_parts)
            
            # If summary is too long, truncate intelligently
            if len(summary) > 100:
                # Try to keep the most important parts
                important_parts = [p for p in summary_parts[:5]]  # Keep first 5 parts
                summary = " | ".join(important_parts)
                if len(summary) > 100:
                    summary = summary[:97] + "..."
                else:
                    summary += " | ..."
            
            self.files_table.item(i, 1).setText(summary)
    
    def get_file_options(self):
        """Get options for all files."""
        return self.file_options.copy()

