"""
Command preview dialog for Faster Whisper GUI.
Shows the command that will be executed and allows copying/editing.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class CommandPreviewDialog(QDialog):
    """Dialog showing the command that will be executed."""
    
    def __init__(self, exe_path, args, parent=None):
        super().__init__(parent)
        self.exe_path = exe_path
        self.args = args
        self.edited_command = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Command Preview")
        self.setMinimumWidth(700)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel("Review the command that will be executed. You can copy it or edit it manually.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Command display
        self.command_text = QTextEdit()
        self.command_text.setReadOnly(False)  # Allow editing
        self.command_text.setFont(QFont("Consolas", 9))
        
        # Build full command string
        full_command = f'"{self.exe_path}" ' + ' '.join(f'"{arg}"' if ' ' in str(arg) else str(arg) for arg in self.args)
        self.command_text.setPlainText(full_command)
        
        layout.addWidget(self.command_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(copy_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        use_edited_btn = QPushButton("Use Edited Command")
        use_edited_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px;")
        use_edited_btn.clicked.connect(self.accept_edited)
        button_layout.addWidget(use_edited_btn)
        
        use_original_btn = QPushButton("Use Original Command")
        use_original_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 5px;")
        use_original_btn.clicked.connect(self.accept)
        button_layout.addWidget(use_original_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def copy_to_clipboard(self):
        """Copy command to clipboard."""
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.command_text.toPlainText())
        QMessageBox.information(self, "Copied", "Command copied to clipboard!")
    
    def accept_edited(self):
        """Accept the edited command."""
        self.edited_command = self.command_text.toPlainText()
        self.accept()
    
    def get_command(self):
        """Get the command (edited or original)."""
        if self.edited_command:
            return self.edited_command
        return f'"{self.exe_path}" ' + ' '.join(f'"{arg}"' if ' ' in str(arg) else str(arg) for arg in self.args)

