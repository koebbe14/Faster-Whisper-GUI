"""
Queue Window for Faster Whisper GUI.
Shows processing queue status during multi-file processing.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from processing_queue import JobStatus


class QueueWindow(QDialog):
    """Window showing the processing queue for multiple files."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing Queue")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the window UI."""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Processing Queue - Files will be processed sequentially")
        header_label.setStyleSheet("font-weight: bold; font-size: 11pt; padding: 10px;")
        layout.addWidget(header_label)
        
        # Queue table
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(4)
        self.queue_table.setHorizontalHeaderLabels(["File", "Status", "Progress", "Output"])
        self.queue_table.horizontalHeader().setStretchLastSection(True)
        self.queue_table.setAlternatingRowColors(True)
        self.queue_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.queue_table)
        
        # Overall progress
        progress_group = QVBoxLayout()
        self.overall_progress_label = QLabel("Overall Progress: 0 / 0 files")
        progress_group.addWidget(self.overall_progress_label)
        
        self.overall_progress_bar = QProgressBar()
        progress_group.addWidget(self.overall_progress_bar)
        
        layout.addLayout(progress_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.pause_btn = QPushButton("Pause Queue")
        self.pause_btn.clicked.connect(self.on_pause_clicked)
        button_layout.addWidget(self.pause_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Close (Processing Continues)")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def setup_queue(self, file_list, file_options):
        """Setup the queue with files and their options."""
        self.file_list = file_list
        self.file_options = file_options
        self.queue_table.setRowCount(len(file_list))
        
        for i, file_path in enumerate(file_list):
            # File name
            file_item = QTableWidgetItem(Path(file_path).name)
            file_item.setFlags(file_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.queue_table.setItem(i, 0, file_item)
            
            # Status
            status_item = QTableWidgetItem("Pending")
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.queue_table.setItem(i, 1, status_item)
            
            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 0)  # Indeterminate
            progress_bar.setVisible(False)
            self.queue_table.setCellWidget(i, 2, progress_bar)
            
            # Output (empty initially)
            output_item = QTableWidgetItem("")
            output_item.setFlags(output_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.queue_table.setItem(i, 3, output_item)
        
        self.queue_table.resizeColumnsToContents()
        self.update_overall_progress()
    
    def update_file_status(self, file_index, status, message=""):
        """Update status for a specific file."""
        status_item = self.queue_table.item(file_index, 1)
        if status_item:
            status_item.setText(status)
            
            # Color coding
            if status == "Completed":
                status_item.setForeground(Qt.GlobalColor.green)
            elif status == "Failed":
                status_item.setForeground(Qt.GlobalColor.red)
            elif status == "Processing":
                status_item.setForeground(Qt.GlobalColor.blue)
                # Show progress bar
                progress_bar = self.queue_table.cellWidget(file_index, 2)
                if progress_bar:
                    progress_bar.setVisible(True)
            else:
                status_item.setForeground(Qt.GlobalColor.black)
                # Hide progress bar
                progress_bar = self.queue_table.cellWidget(file_index, 2)
                if progress_bar:
                    progress_bar.setVisible(False)
        
        if message:
            output_item = self.queue_table.item(file_index, 3)
            if output_item:
                output_item.setText(message)
        
        self.update_overall_progress()
    
    def update_overall_progress(self):
        """Update overall progress display."""
        total = self.queue_table.rowCount()
        completed = sum(1 for i in range(total) 
                       if self.queue_table.item(i, 1).text() == "Completed")
        processing = sum(1 for i in range(total) 
                        if self.queue_table.item(i, 1).text() == "Processing")
        failed = sum(1 for i in range(total) 
                    if self.queue_table.item(i, 1).text() == "Failed")
        
        self.overall_progress_label.setText(
            f"Overall Progress: {completed} completed, {processing} processing, "
            f"{failed} failed, {total - completed - processing - failed} pending out of {total} files"
        )
        
        if total > 0:
            self.overall_progress_bar.setMaximum(total)
            self.overall_progress_bar.setValue(completed)
    
    def on_pause_clicked(self):
        """Handle pause button click."""
        # Signal parent to toggle pause
        if hasattr(self.parent(), 'toggle_queue_pause'):
            self.parent().toggle_queue_pause()
    
    def get_file_index(self, file_path):
        """Get table index for a file path."""
        for i, f in enumerate(self.file_list):
            if f == file_path:
                return i
        return -1

