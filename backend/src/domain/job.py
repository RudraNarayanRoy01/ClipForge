import uuid
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from typing import Optional, Dict, Any


class JobStatus(str, Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    """
    Aggregate Root representing an asynchronous workflow execution.
    Encapsulates state transitions and ensures lifecycle validity.
    """
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = "Unknown Task"
    status: JobStatus = JobStatus.REQUESTED
    previous_status: Optional[JobStatus] = None
    
    # Observability
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status_updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # State flags
    cancellation_requested: bool = False
    
    # Retry policy
    retry_count: int = 0
    max_retries: int = 3
    
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def _transition_to(self, new_status: JobStatus) -> None:
        """Internal helper to manage deterministic state transitions and observability."""
        self.previous_status = self.status
        self.status = new_status
        self.status_updated_at = datetime.now(timezone.utc)

    def accept(self) -> None:
        if self.status != JobStatus.REQUESTED:
            raise ValueError(f"Cannot accept job in state {self.status}")
        self._transition_to(JobStatus.ACCEPTED)

    def queue(self) -> None:
        if self.status not in (JobStatus.ACCEPTED, JobStatus.FAILED):
            raise ValueError(f"Cannot queue job from state {self.status}")
        self._transition_to(JobStatus.QUEUED)

    def start(self) -> None:
        if self.status != JobStatus.QUEUED:
            raise ValueError(f"Cannot start job from state {self.status}")
        if self.cancellation_requested:
            raise ValueError("Cannot start a job that has a pending cancellation request")
            
        self._transition_to(JobStatus.RUNNING)
        if self.started_at is None:
            self.started_at = datetime.now(timezone.utc)

    def complete(self, result: Optional[Dict[str, Any]] = None) -> None:
        if self.status != JobStatus.RUNNING:
            raise ValueError(f"Cannot complete job in state {self.status}")
        if self.cancellation_requested:
            raise ValueError("Cannot complete a job that has been requested to cancel. Must be cancelled.")
            
        self._transition_to(JobStatus.COMPLETED)
        self.completed_at = datetime.now(timezone.utc)
        self.result = result

    def fail(self, error: str) -> None:
        if self.status in (JobStatus.COMPLETED, JobStatus.CANCELLED):
            raise ValueError(f"Cannot fail job that is already {self.status}")
            
        self._transition_to(JobStatus.FAILED)
        self.completed_at = datetime.now(timezone.utc)
        self.error = error

    @property
    def is_retry_eligible(self) -> bool:
        return self.status == JobStatus.FAILED and self.retry_count < self.max_retries and not self.cancellation_requested

    def retry(self) -> None:
        if not self.is_retry_eligible:
            raise ValueError(f"Job is not eligible for retry. Status: {self.status}, Retries: {self.retry_count}/{self.max_retries}")
        self.retry_count += 1
        self.error = None
        self.completed_at = None
        self.queue()

    def request_cancellation(self) -> None:
        if self.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            raise ValueError(f"Cannot request cancellation for job in terminal state {self.status}")
        self.cancellation_requested = True

    def cancel(self) -> None:
        """Finalizes the cancellation after cleanup"""
        if self.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED) and not self.cancellation_requested:
             # Can directly cancel if requested, accepted, or queued.
             if self.status != JobStatus.CANCELLED:
                 pass # We allow it to bypass if it wasn't running
        if self.status in (JobStatus.COMPLETED, JobStatus.CANCELLED):
            raise ValueError(f"Cannot cancel job in state {self.status}")
            
        self._transition_to(JobStatus.CANCELLED)
        self.completed_at = datetime.now(timezone.utc)
