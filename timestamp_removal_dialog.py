"""
Timestamp removal dialog for Faster Whisper GUI.
Allows users to preview output files and remove timestamps, then save modified versions.
"""

import re
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMessageBox, QFileDialog, QTextEdit, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class TimestampRemovalDialog(QDialog):
    """Dialog for removing timestamps from output files."""
    
    def __init__(self, output_file_path, parent=None):
        super().__init__(parent)
        self.output_file_path = Path(output_file_path)
        self.original_content = ""
        self.init_ui()
        self.load_output_file()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Remove Timestamps")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Preview the output file below. You can remove timestamp markers from the file and save a clean version. "
            "Check 'Remove timestamps when saving' to remove all timestamp markers, then click 'Preview Changes' to see "
            "how it will look, and finally 'Save to New File' to create the updated file without timestamps."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # File path display
        file_label = QLabel(f"File: {self.output_file_path.name}")
        file_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(file_label)
        
        # Full content preview (scrollable)
        content_label = QLabel("File Content (scroll to review):")
        layout.addWidget(content_label)
        
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        self.content_text.setFont(QFont("Consolas", 9))
        self.content_text.setMinimumHeight(400)
        layout.addWidget(self.content_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        preview_btn = QPushButton("Preview Changes")
        preview_btn.clicked.connect(self.preview_changes)
        button_layout.addWidget(preview_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Remove timestamps checkbox
        self.remove_timestamps_check = QCheckBox("Remove timestamps when saving")
        self.remove_timestamps_check.setToolTip("Remove timestamp markers from the output file")
        button_layout.addWidget(self.remove_timestamps_check)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("Save to New File")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px;")
        save_btn.clicked.connect(self.save_to_new_file)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_output_file(self):
        """Load the output file content."""
        try:
            if not self.output_file_path.exists():
                QMessageBox.warning(self, "File Not Found", f"Output file not found: {self.output_file_path}")
                self.reject()
                return
            
            # Read file content
            with open(self.output_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.original_content = f.read()
            
            if not self.original_content.strip():
                QMessageBox.warning(self, "Empty File", "The output file is empty.")
                self.reject()
                return
            
            # Display original content
            self.content_text.setPlainText(self.original_content)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
            self.reject()
    
    def remove_timestamps_from_content(self, content):
        """Remove timestamp markers from content."""
        # Detect file format based on content
        file_ext = self.output_file_path.suffix.lower()
        
        if file_ext == '.srt':
            # SRT format: Remove subtitle index, timestamps, and keep only text
            # Pattern: number, timestamp line, text line(s), blank line
            lines = content.split('\n')
            cleaned_lines = []
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                # Skip subtitle index (number)
                if line.isdigit():
                    i += 1
                    # Skip timestamp line (00:00:00,000 --> 00:00:05,000)
                    if i < len(lines):
                        timestamp_line = lines[i].strip()
                        if '-->' in timestamp_line:
                            i += 1
                            # Collect text lines until blank line
                            text_lines = []
                            while i < len(lines) and lines[i].strip():
                                text_lines.append(lines[i].strip())
                                i += 1
                            if text_lines:
                                cleaned_lines.append(' '.join(text_lines))
                            # Skip blank line
                            if i < len(lines) and not lines[i].strip():
                                i += 1
                            continue
                # If not part of SRT structure, keep the line if it has content
                if line and not re.match(r'^\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}$', line):
                    cleaned_lines.append(line)
                i += 1
            return '\n'.join(cleaned_lines)
        
        elif file_ext == '.vtt':
            # VTT format: Remove WEBVTT header, timestamps, and keep only text
            lines = content.split('\n')
            cleaned_lines = []
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                # Skip WEBVTT header and metadata
                if line.startswith('WEBVTT') or line.startswith('NOTE') or not line:
                    i += 1
                    continue
                # Skip timestamp line (00:00:00.000 --> 00:00:05.000)
                if '-->' in line:
                    i += 1
                    # Collect text lines until blank line or next timestamp
                    text_lines = []
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if not next_line or '-->' in next_line:
                            break
                        if not next_line.startswith('NOTE'):
                            text_lines.append(next_line)
                        i += 1
                    if text_lines:
                        cleaned_lines.append(' '.join(text_lines))
                    continue
                # Keep other content
                if line:
                    cleaned_lines.append(line)
                i += 1
            return '\n'.join(cleaned_lines)
        
        else:
            # Text format: Remove various timestamp patterns
            # Pattern 1: [00:00:00.000 --> 00:00:05.000] or [00:00:00,000 --> 00:00:05,000]
            timestamp_pattern1 = r'\[\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}\]\s*'
            content = re.sub(timestamp_pattern1, '', content)
            
            # Pattern 2: [00:00:00.000] word [00:00:01.000] word (word-level timestamps)
            timestamp_pattern2 = r'\[\d{2}:\d{2}:\d{2}[,.]\d{3}\]\s*'
            content = re.sub(timestamp_pattern2, '', content)
            
            # Pattern 3: [00:02.100 --> 00:08.280] (short format)
            timestamp_pattern3 = r'\[\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}\.\d{3}\]\s*'
            content = re.sub(timestamp_pattern3, '', content)
            
            # Pattern 4: [00:02.100] (short format word timestamps)
            timestamp_pattern4 = r'\[\d{2}:\d{2}\.\d{3}\]\s*'
            content = re.sub(timestamp_pattern4, '', content)
            
            # Clean up extra whitespace
            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                # Remove multiple spaces
                line = re.sub(r'\s+', ' ', line)
                if line:  # Skip empty lines
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
    
    def preview_changes(self):
        """Preview the changes with timestamps removed."""
        if not self.remove_timestamps_check.isChecked():
            QMessageBox.information(
                self, 
                "No Changes", 
                "Please check 'Remove timestamps when saving' to preview changes."
            )
            return
        
        # Remove timestamps
        modified_content = self.remove_timestamps_from_content(self.original_content)
        
        # Show preview
        self.content_text.setPlainText(modified_content)
        
        QMessageBox.information(
            self,
            "Preview",
            "Preview updated. Review the content above. Click 'Save to New File' to save the changes."
        )
    
    def save_to_new_file(self):
        """Save the modified content to a new file."""
        if not self.remove_timestamps_check.isChecked():
            QMessageBox.warning(
                self, 
                "No Changes", 
                "Please check 'Remove timestamps when saving' to save a modified file."
            )
            return
        
        # Get save location
        default_name = self.output_file_path.stem + "_no_timestamps" + self.output_file_path.suffix
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File Without Timestamps",
            str(self.output_file_path.parent / default_name),
            f"All Files (*.*);;Text Files (*.txt);;SRT Files (*.srt);;VTT Files (*.vtt)"
        )
        
        if not save_path:
            return
        
        try:
            # Remove timestamps
            modified_content = self.remove_timestamps_from_content(self.original_content)
            
            # Save to new file
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            QMessageBox.information(
                self, 
                "Success", 
                f"File saved successfully!\n\nSaved to: {save_path}\n\nTimestamps removed."
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

