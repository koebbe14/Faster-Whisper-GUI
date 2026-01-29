"""
Processing queue manager for Faster Whisper GUI.
Manages a queue of transcription jobs with different settings.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class JobStatus(Enum):
    """Status of a job in the queue."""
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"
    PAUSED = "Paused"


@dataclass
class QueueJob:
    """Represents a single job in the processing queue."""
    job_id: int
    input_files: List[str]
    output_dir: str
    options: dict
    status: JobStatus = JobStatus.PENDING
    error_message: Optional[str] = None
    output_files: List[str] = None
    
    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []


class ProcessingQueue:
    """Manages a queue of transcription jobs."""
    
    def __init__(self):
        self.jobs: List[QueueJob] = []
        self.current_job_index: int = -1
        self.is_paused: bool = False
        self.next_job_id: int = 1
    
    def add_job(self, input_files: List[str], output_dir: str, options: dict) -> QueueJob:
        """Add a new job to the queue."""
        job = QueueJob(
            job_id=self.next_job_id,
            input_files=input_files,
            output_dir=output_dir,
            options=options
        )
        self.jobs.append(job)
        self.next_job_id += 1
        return job
    
    def get_next_job(self) -> Optional[QueueJob]:
        """Get the next pending job."""
        if self.is_paused:
            return None
        
        for i, job in enumerate(self.jobs):
            if job.status == JobStatus.PENDING:
                self.current_job_index = i
                return job
        
        return None
    
    def get_current_job(self) -> Optional[QueueJob]:
        """Get the currently processing job."""
        if 0 <= self.current_job_index < len(self.jobs):
            return self.jobs[self.current_job_index]
        return None
    
    def mark_job_processing(self, job: QueueJob):
        """Mark a job as processing."""
        job.status = JobStatus.PROCESSING
    
    def mark_job_completed(self, job: QueueJob, output_files: List[str] = None):
        """Mark a job as completed."""
        job.status = JobStatus.COMPLETED
        if output_files:
            job.output_files = output_files
    
    def mark_job_failed(self, job: QueueJob, error_message: str):
        """Mark a job as failed."""
        job.status = JobStatus.FAILED
        job.error_message = error_message
    
    def mark_job_cancelled(self, job: QueueJob):
        """Mark a job as cancelled."""
        job.status = JobStatus.CANCELLED
    
    def pause(self):
        """Pause the queue."""
        self.is_paused = True
    
    def resume(self):
        """Resume the queue."""
        self.is_paused = False
    
    def clear_completed(self):
        """Remove completed jobs from the queue."""
        self.jobs = [job for job in self.jobs if job.status != JobStatus.COMPLETED]
    
    def clear_all(self):
        """Clear all jobs from the queue."""
        self.jobs = []
        self.current_job_index = -1
    
    def get_pending_count(self) -> int:
        """Get count of pending jobs."""
        return sum(1 for job in self.jobs if job.status == JobStatus.PENDING)
    
    def get_completed_count(self) -> int:
        """Get count of completed jobs."""
        return sum(1 for job in self.jobs if job.status == JobStatus.COMPLETED)
    
    def get_failed_count(self) -> int:
        """Get count of failed jobs."""
        return sum(1 for job in self.jobs if job.status == JobStatus.FAILED)
    
    def has_pending_jobs(self) -> bool:
        """Check if there are any pending jobs."""
        return self.get_pending_count() > 0
    
    def remove_job(self, job: QueueJob):
        """Remove a job from the queue."""
        if job in self.jobs:
            self.jobs.remove(job)
            if self.current_job_index >= len(self.jobs):
                self.current_job_index = -1

