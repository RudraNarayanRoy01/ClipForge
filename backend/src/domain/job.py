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
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def accept(self) -> None:
        if self.status != JobStatus.REQUESTED:
            raise ValueError(f"Cannot accept job in state {self.status}")
        self.status = JobStatus.ACCEPTED

    def queue(self) -> None:
        if self.status != JobStatus.ACCEPTED:
            raise ValueError(f"Cannot queue job in state {self.status}")
        self.status = JobStatus.QUEUED

    def start(self) -> None:
        if self.status != JobStatus.QUEUED:
            raise ValueError(f"Cannot start job from state {self.status}")
        self.status = JobStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)

    def complete(self, result: Optional[Dict[str, Any]] = None) -> None:
        if self.status != JobStatus.RUNNING:
            raise ValueError(f"Cannot complete job in state {self.status}")
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.result = result

    def fail(self, error: str) -> None:
        # A job might fail while queued or running
        if self.status in (JobStatus.COMPLETED, JobStatus.CANCELLED):
            raise ValueError(f"Cannot fail job that is already {self.status}")
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now(timezone.utc)
        self.error = error

    def cancel(self) -> None:
        if self.status in (JobStatus.COMPLETED, JobStatus.FAILED):
            raise ValueError(f"Cannot cancel job in state {self.status}")
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.now(timezone.utc)
