"""
Speaker replacement dialog for Faster Whisper GUI.
Allows users to preview diarization output and replace speaker labels with custom names.
"""

import re
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox,
    QFileDialog, QHeaderView, QTextEdit, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SpeakerReplacementDialog(QDialog):
    """Dialog for replacing speaker labels with custom names."""
    
    def __init__(self, output_file_path, parent=None):
        super().__init__(parent)
        self.output_file_path = Path(output_file_path)
        self.speaker_mapping = {}
        self.init_ui()
        self.load_output_file()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Speaker Identification & Replacement")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Review the diarized transcript below. The system has identified different speakers in your audio. "
            "You can replace the generic speaker labels (SPEAKER_00, SPEAKER_01, etc.) with actual names or descriptions. "
            "Enter the replacement names in the 'Replace With' column, then click 'Preview Changes' to see how it will look, "
            "and finally 'Save to New File' to create the updated transcript with custom speaker names."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # Speaker mapping table
        table_label = QLabel("Speaker Labels Found (enter replacement names in the 'Replace With' column):")
        layout.addWidget(table_label)
        
        self.speaker_table = QTableWidget()
        self.speaker_table.setColumnCount(2)
        self.speaker_table.setHorizontalHeaderLabels(["Original Label", "Replace With"])
        self.speaker_table.horizontalHeader().setStretchLastSection(True)
        self.speaker_table.setAlternatingRowColors(True)
        self.speaker_table.setMaximumHeight(150)
        layout.addWidget(self.speaker_table)
        
        # Full transcript preview (scrollable)
        transcript_label = QLabel("Full Transcript (scroll to review and identify speakers):")
        layout.addWidget(transcript_label)
        
        self.full_transcript_text = QTextEdit()
        self.full_transcript_text.setReadOnly(True)
        self.full_transcript_text.setFont(QFont("Consolas", 9))
        self.full_transcript_text.setMinimumHeight(300)
        layout.addWidget(self.full_transcript_text)
        
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
        self.remove_timestamps_check.setToolTip("Remove timestamp markers like [00:02.100 --> 00:08.280] from the output")
        button_layout.addWidget(self.remove_timestamps_check)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("Save to New File")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px;")
        save_btn.clicked.connect(self.save_to_new_file)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_output_file(self):
        """Load the output file and extract speaker labels."""
        try:
            if not self.output_file_path.exists():
                QMessageBox.warning(self, "File Not Found", f"Output file not found: {self.output_file_path}")
                self.speaker_table.setRowCount(0)
                self.original_content = ""
                self.full_transcript_text.setPlainText("")
                return
            
            with open(self.output_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check if content is empty
            if not content or not content.strip():
                QMessageBox.warning(
                    self, 
                    "Empty File", 
                    "The output file is empty or contains no content."
                )
                self.speaker_table.setRowCount(0)
                self.original_content = ""
                self.full_transcript_text.setPlainText("")
                return
            
            # Find all speaker labels (SPEAKER_00, SPEAKER_01, SPEAKER_0, SPEAKER_1, etc.)
            # Also handle variations like SPEAKER, SPEAKER_00, SPEAKER_01, SPEAKER_0, SPEAKER_1
            speaker_pattern = r'SPEAKER(?:_(\d+))?'
            matches = re.findall(speaker_pattern, content, re.IGNORECASE)
            speakers = set()
            for match in matches:
                if match:  # Has number (SPEAKER_00, SPEAKER_01, etc.)
                    speakers.add(match)
                else:  # Just "SPEAKER" without number
                    speakers.add("0")  # Treat as SPEAKER_0
            
            # If no numbered speakers found, check for just "SPEAKER" pattern
            if not speakers or (len(speakers) == 1 and "0" in speakers and len(content.split("SPEAKER")) < 3):
                # Look for any SPEAKER pattern more broadly
                speaker_pattern2 = r'(SPEAKER(?:_\d+)?)'
                speaker_labels = set(re.findall(speaker_pattern2, content, re.IGNORECASE))
                if speaker_labels and len(speaker_labels) > 1:  # More than just one "SPEAKER"
                    speakers = set()
                    for label in speaker_labels:
                        num_match = re.search(r'_(\d+)', label, re.IGNORECASE)
                        if num_match:
                            speakers.add(num_match.group(1))
                        else:
                            speakers.add("0")
            
            # Sort speakers numerically
            if speakers:
                speakers = sorted(speakers, key=int)
            else:
                # No speakers found - might be a different format
                QMessageBox.warning(
                    self, 
                    "No Speakers Found", 
                    "No speaker labels (SPEAKER_XX) were found in the file. "
                    "The file may not contain diarization output, or it may use a different format.\n\n"
                    "The transcript will still be shown, but you won't be able to replace speaker labels."
                )
                # Still show the content even if no speakers found
                self.original_content = content
                self.full_transcript_text.setPlainText(content)
                return
            
            # Populate table
            self.speaker_table.setRowCount(len(speakers))
            self.speaker_mapping = {}
            
            for i, speaker_num in enumerate(speakers):
                # Convert to int for formatting (speaker_num is a string from regex)
                speaker_int = int(speaker_num)
                label = f"SPEAKER_{speaker_int:02d}"
                
                # Original label (read-only)
                label_item = QTableWidgetItem(label)
                label_item.setFlags(label_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.speaker_table.setItem(i, 0, label_item)
                
                # Replacement field
                replace_item = QTableWidgetItem("")
                self.speaker_table.setItem(i, 1, replace_item)
                
                self.speaker_mapping[label] = ""
            
            # Store original content
            self.original_content = content
            
            # Show full transcript in the preview area
            self.full_transcript_text.setPlainText(content)
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to load file: {str(e)}\n\nDetails:\n{error_details}"
            )
            # Ensure table is empty if loading failed
            self.speaker_table.setRowCount(0)
            self.original_content = ""
            self.full_transcript_text.setPlainText("")
    
    def get_replacements(self):
        """Get current replacement mappings from table."""
        replacements = {}
        for i in range(self.speaker_table.rowCount()):
            original_item = self.speaker_table.item(i, 0)
            replacement_item = self.speaker_table.item(i, 1)
            
            # Check if items exist (they might be None if table wasn't properly populated)
            if original_item is None or replacement_item is None:
                continue
            
            original = original_item.text()
            replacement = replacement_item.text().strip()
            if replacement:
                replacements[original] = replacement
        return replacements
    
    def preview_changes(self):
        """Preview the changes with replacements applied."""
        replacements = self.get_replacements()
        
        # Check if user wants to preview timestamp removal only
        if not replacements and not self.remove_timestamps_check.isChecked():
            QMessageBox.information(
                self, 
                "No Changes", 
                "No replacements specified and timestamp removal is not enabled. "
                "Enter names in the 'Replace With' column or check 'Remove timestamps when saving'."
            )
            return
        
        # Apply replacements
        modified_content = self.original_content
        if replacements:
            for original, replacement in replacements.items():
                # Replace all occurrences (case-insensitive)
                modified_content = re.sub(
                    re.escape(original),
                    replacement,
                    modified_content,
                    flags=re.IGNORECASE
                )
        
        # Remove timestamps if checkbox is checked
        if self.remove_timestamps_check.isChecked():
            modified_content = self.remove_timestamps_from_content(modified_content)
        
        # Show preview in the full transcript area
        self.full_transcript_text.setPlainText(modified_content)
    
    def remove_timestamps_from_content(self, content):
        """Remove timestamp markers from content."""
        # Pattern to match timestamps like [00:02.100 --> 00:08.280]
        timestamp_pattern = r'\[\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}\.\d{3}\]\s*'
        # Remove timestamps
        content = re.sub(timestamp_pattern, '', content)
        # Clean up extra whitespace
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)
    
    def save_to_new_file(self):
        """Save the modified content to a new file."""
        replacements = self.get_replacements()
        
        # Check if user wants to save with timestamp removal only
        if not replacements and not self.remove_timestamps_check.isChecked():
            QMessageBox.warning(
                self, 
                "No Changes", 
                "Please specify at least one replacement or check 'Remove timestamps when saving' before saving."
            )
            return
        
        # Determine default filename based on what's being done
        if replacements:
            default_name = self.output_file_path.stem + "_renamed" + self.output_file_path.suffix
        else:
            default_name = self.output_file_path.stem + "_no_timestamps" + self.output_file_path.suffix
        
        # Get save location
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Modified File",
            str(self.output_file_path.parent / default_name),
            f"All Files (*.*);;Text Files (*.txt);;SRT Files (*.srt);;VTT Files (*.vtt)"
        )
        
        if not save_path:
            return
        
        try:
            # Apply replacements
            modified_content = self.original_content
            if replacements:
                for original, replacement in replacements.items():
                    modified_content = re.sub(
                        re.escape(original),
                        replacement,
                        modified_content,
                        flags=re.IGNORECASE
                    )
            
            # Remove timestamps if requested
            if self.remove_timestamps_check.isChecked():
                modified_content = self.remove_timestamps_from_content(modified_content)
            
            # Save to new file
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            # Build success message
            message = f"File saved successfully!\n\nSaved to: {save_path}\n\n"
            if replacements:
                message += f"Replacements made:\n" + "\n".join(f"  {orig} → {repl}" for orig, repl in replacements.items())
                if self.remove_timestamps_check.isChecked():
                    message += "\n\nTimestamps removed."
            elif self.remove_timestamps_check.isChecked():
                message += "Timestamps removed."
            
            QMessageBox.information(self, "Success", message)
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

