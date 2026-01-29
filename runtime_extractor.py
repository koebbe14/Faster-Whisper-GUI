"""
Runtime file extraction for Faster Whisper GUI.
Extracts bundled files to user data directory on first run.
"""

import os
import sys
import zipfile
from pathlib import Path
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import QThread, pyqtSignal


def get_user_data_dir():
    """Get the user-specific data directory."""
    appdata_local = os.getenv('LOCALAPPDATA', os.path.expanduser('~'))
    user_data_dir = Path(appdata_local) / "FasterWhisperGUI"
    user_data_dir.mkdir(parents=True, exist_ok=True)
    return user_data_dir


def needs_extraction():
    """Check if files need to be extracted."""
    user_data_dir = get_user_data_dir()
    return not (
        (user_data_dir / "_xxl_data").exists() and
        (user_data_dir / "faster-whisper-xxl.exe").exists() and
        (user_data_dir / "ffmpeg.exe").exists()
    )


class ExtractionThread(QThread):
    """Thread for extracting files in the background."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def run(self):
        try:
            user_data_dir = get_user_data_dir()
            
            # Find bundled ZIP file
            if hasattr(sys, '_MEIPASS'):
                zip_path = Path(sys._MEIPASS) / "runtime_files.zip"
            else:
                # For development/testing
                zip_path = Path(__file__).parent / "runtime_files.zip"
            
            if not zip_path.exists():
                self.finished.emit(False, f"Runtime files ZIP not found at {zip_path}")
                return
            
            # Extract files
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                total_files = len(file_list)
                
                for i, file_name in enumerate(file_list):
                    zip_ref.extract(file_name, user_data_dir)
                    progress = int((i + 1) / total_files * 100)
                    self.progress.emit(progress)
            
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))


class ExtractionDialog(QDialog):
    """Dialog shown during first-run extraction."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("First-Time Setup")
        self.setMinimumWidth(400)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~self.windowFlags().WindowContextHelpButtonHint)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QLabel(
            "Extracting required files to your user directory.\n\n"
            "This only happens once and may take a few minutes.\n"
            "Please wait..."
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        self.status_label = QLabel("Preparing...")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Start extraction
        self.extraction_thread = ExtractionThread()
        self.extraction_thread.progress.connect(self.progress.setValue)
        self.extraction_thread.finished.connect(self.on_extraction_finished)
        self.extraction_thread.start()
    
    def on_extraction_finished(self, success, error_msg):
        if success:
            self.status_label.setText("Extraction complete! Starting application...")
            self.accept()
        else:
            self.status_label.setText(f"Error: {error_msg}\n\nPlease check that you have write access to:\n{get_user_data_dir()}")
            # Keep dialog open so user can read the error


def ensure_runtime_files(parent_window=None):
    """Ensure runtime files are extracted. Show dialog if extraction needed."""
    if needs_extraction():
        dialog = ExtractionDialog(parent_window)
        result = dialog.exec()
        
        # Verify extraction succeeded
        if needs_extraction():
            from PyQt6.QtWidgets import QMessageBox
            error_msg = (
                "Failed to extract required files.\n\n"
                f"Please check that you have write access to:\n{get_user_data_dir()}\n\n"
                "The application cannot continue without these files."
            )
            msg = QMessageBox(parent_window)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Extraction Failed")
            msg.setText(error_msg)
            msg.exec()
            return False
        
        return True
    
    return True

