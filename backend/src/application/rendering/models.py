import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import List, Optional, Any, Dict
from src.domain.render_plan import RenderPlan


class RenderJobStatus(Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class RenderJobPriority(Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class RenderJobId:
    value: uuid.UUID

    @classmethod
    def generate(cls) -> "RenderJobId":
        return cls(value=uuid.uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class RenderJobMetadata:
    """
    Contextual request information.
    Does NOT contain execution history, progress, worker identifiers, or diagnostics.
    """
    project_id: uuid.UUID
    created_at: datetime
    requester: str
    output_profile: str
    campaign_id: Optional[uuid.UUID] = None
    tags: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass(frozen=True)
class RenderJob:
    """
    The RenderJob Aggregate Root.
    Immutable application-layer model representing a render orchestration job.
    """
    id: RenderJobId
    plan: RenderPlan
    status: RenderJobStatus
    priority: RenderJobPriority
    metadata: RenderJobMetadata
    schema_version: str = "1.0"

    def update_status(self, new_status: RenderJobStatus) -> "RenderJob":
        """Copy-on-write semantics for state evolution."""
        return RenderJob(
            id=self.id,
            plan=self.plan,
            status=new_status,
            priority=self.priority,
            metadata=self.metadata,
            schema_version=self.schema_version,
        )

    def update_priority(self, new_priority: RenderJobPriority) -> "RenderJob":
        """Copy-on-write semantics for priority evolution."""
        return RenderJob(
            id=self.id,
            plan=self.plan,
            status=self.status,
            priority=new_priority,
            metadata=self.metadata,
            schema_version=self.schema_version,
        )


class RenderStage(Enum):
    """Canonical logical stages for rendering."""
    INITIALIZING = "INITIALIZING"
    LOADING_ASSETS = "LOADING_ASSETS"
    BUILDING_TIMELINE = "BUILDING_TIMELINE"
    COMPOSITING = "COMPOSITING"
    ENCODING = "ENCODING"
    FINALIZING = "FINALIZING"
    COMPLETED = "COMPLETED"


@dataclass(frozen=True)
class RenderProgress:
    """
    Immutable application-layer model representing render execution progress.
    """
    job_id: RenderJobId
    stage: RenderStage
    percentage: float
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        # Validation for internally consistent progress
        if not (0.0 <= self.percentage <= 100.0):
            raise ValueError(f"Percentage must be between 0.0 and 100.0, got {self.percentage}")
        
        if self.stage == RenderStage.COMPLETED and self.percentage != 100.0:
            raise ValueError(f"COMPLETED stage implies 100.0% percentage, got {self.percentage}%")


class CancellationResult(Enum):
    """Result of a cancellation request."""
    NOT_REQUESTED = "NOT_REQUESTED"
    REQUESTED = "REQUESTED"
    CANCELLED = "CANCELLED"
    CANCELLATION_REJECTED = "CANCELLATION_REJECTED"


@dataclass(frozen=True)
class RenderCancellationToken:
    """
    Immutable value object expressing cancellation intent and identity.
    Backend-neutral and safe to pass across process boundaries.
    """
    job_id: RenderJobId
    is_cancelled: bool = False
    reason: Optional[str] = None
    requested_at: datetime = field(default_factory=datetime.utcnow)

    def request_cancellation(self) -> "RenderCancellationToken":
        """
        Returns a new token with cancellation requested.
        Useful for pure immutable state transitions.
        """
        return RenderCancellationToken(
            job_id=self.job_id,
            is_cancelled=True,
            reason=self.reason,
            requested_at=datetime.utcnow()
        )
