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
