"""
Process manager for Faster Whisper GUI.
Handles subprocess execution with real-time output capture using QThread.
"""

import subprocess
import sys
from PyQt6.QtCore import QThread, pyqtSignal


class ProcessWorker(QThread):
    """Worker thread for running faster-whisper-xxl.exe subprocess."""
    
    # Signals for communication with main thread
    output_received = pyqtSignal(str)  # Emitted when output line is received
    error_received = pyqtSignal(str)  # Emitted when error line is received
    finished = pyqtSignal(int)  # Emitted when process finishes (exit code)
    error_occurred = pyqtSignal(str)  # Emitted on process errors
    
    def __init__(self, exe_path, args):
        """
        Initialize process worker.
        
        Args:
            exe_path: Path to faster-whisper-xxl.exe
            args: List of command-line arguments
        """
        super().__init__()
        self.exe_path = exe_path
        self.args = args
        self.process = None
        self._is_cancelled = False
    
    def run(self):
        """Execute the subprocess and capture output."""
        try:
            # Build full command
            cmd = [self.exe_path] + self.args
            
            # Start process with real-time output capture
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout
                universal_newlines=True,
                bufsize=1,  # Line buffered
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            # Read output line by line
            for line in iter(self.process.stdout.readline, ''):
                if self._is_cancelled:
                    self.process.terminate()
                    break
                
                if line:
                    # Remove trailing newline and emit signal
                    line = line.rstrip('\n\r')
                    self.output_received.emit(line)
            
            # Wait for process to complete
            if not self._is_cancelled:
                return_code = self.process.wait()
                self.finished.emit(return_code)
            else:
                self.finished.emit(-1)  # Cancelled
                
        except FileNotFoundError:
            self.error_occurred.emit(f"Executable not found: {self.exe_path}")
            self.finished.emit(-1)
        except Exception as e:
            self.error_occurred.emit(f"Error running process: {str(e)}")
            self.finished.emit(-1)
    
    def cancel(self):
        """Cancel the running process."""
        self._is_cancelled = True
        if self.process:
            try:
                self.process.terminate()
            except:
                pass


class ProcessManager:
    """Manages subprocess execution for Faster Whisper."""
    
    def __init__(self):
        self.worker = None
    
    def start_process(self, exe_path, args, output_callback, error_callback, finished_callback, error_occurred_callback):
        """
        Start a subprocess with callbacks.
        
        Args:
            exe_path: Path to executable
            args: Command-line arguments
            output_callback: Function to call with each output line
            error_callback: Function to call with error lines (can be same as output_callback)
            finished_callback: Function to call when process finishes (receives exit code)
            error_occurred_callback: Function to call on process errors (receives error message)
        
        Returns:
            ProcessWorker instance
        """
        # Stop any existing process
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
        
        # Create new worker
        self.worker = ProcessWorker(exe_path, args)
        
        # Connect signals
        self.worker.output_received.connect(output_callback)
        self.worker.error_received.connect(error_callback)
        self.worker.finished.connect(finished_callback)
        self.worker.error_occurred.connect(error_occurred_callback)
        
        # Start worker thread
        self.worker.start()
        
        return self.worker
    
    def stop_process(self):
        """Stop the currently running process."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
    
    def is_running(self):
        """Check if a process is currently running."""
        return self.worker is not None and self.worker.isRunning()

