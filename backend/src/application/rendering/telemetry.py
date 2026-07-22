import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Mapping, Any, Optional, Tuple, Dict
from types import MappingProxyType

from src.application.rendering.models import RenderJobId


class RenderEventType(Enum):
    """
    Canonical application event vocabulary for render execution telemetry.
    Backend-neutral application lifecycle terminology.
    """
    JOB_CREATED = "JOB_CREATED"
    VALIDATED = "VALIDATED"
    STARTED = "STARTED"
    PROGRESS_UPDATED = "PROGRESS_UPDATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLATION_REQUESTED = "CANCELLATION_REQUESTED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class RenderExecutionEvent:
    """
    Immutable application-layer model representing a factual event in the execution lifecycle.
    UUIDs uniquely identify events, but chronological ordering is determined by
    the immutable history sequence and timestamps.
    """
    event_id: uuid.UUID
    job_id: RenderJobId
    event_type: RenderEventType
    timestamp: datetime
    message: str
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    @classmethod
    def create(
        cls,
        job_id: RenderJobId,
        event_type: RenderEventType,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> "RenderExecutionEvent":
        """Factory method to ensure metadata is converted to an immutable MappingProxyType."""
        return cls(
            event_id=uuid.uuid4(),
            job_id=job_id,
            event_type=event_type,
            timestamp=timestamp or datetime.utcnow(),
            message=message,
            metadata=MappingProxyType(metadata or {})
        )


@dataclass(frozen=True)
class RenderExecutionHistory:
    """
    Immutable execution history container representing the sequence of telemetry events.
    Serves as the canonical telemetry source. Event addition follows copy-on-write semantics.
    """
    job_id: RenderJobId
    events: Tuple[RenderExecutionEvent, ...] = field(default_factory=tuple)

    def record_event(self, event: RenderExecutionEvent) -> "RenderExecutionHistory":
        """
        Returns a new RenderExecutionHistory with the event appended.
        Enforces chronological consistency: the new event cannot precede the latest recorded event.
        """
        if event.job_id != self.job_id:
            raise ValueError(f"Event job_id {event.job_id} does not match history job_id {self.job_id}")

        if self.events:
            last_event = self.events[-1]
            if event.timestamp < last_event.timestamp:
                raise ValueError("Chronological inconsistency: Event timestamp precedes the latest recorded event.")

        new_events = self.events + (event,)
        return RenderExecutionHistory(job_id=self.job_id, events=new_events)

    def to_dict(self) -> Dict[str, Any]:
        """Supports serialization for future storage backends."""
        return {
            "job_id": str(self.job_id),
            "events": [
                {
                    "event_id": str(e.event_id),
                    "event_type": e.event_type.value,
                    "timestamp": e.timestamp.isoformat(),
                    "message": e.message,
                    "metadata": dict(e.metadata)
                } for e in self.events
            ]
        }


@dataclass(frozen=True)
class RenderExecutionMetrics:
    """
    Immutable dataclass summarizing execution.
    This is a derived projection created primarily through from_history(...)
    rather than as an independently authoritative model.
    """
    job_id: RenderJobId
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    outcome: str = "PENDING"
    failure_reason: Optional[str] = None

    @classmethod
    def from_history(cls, history: RenderExecutionHistory) -> "RenderExecutionMetrics":
        """
        Derives summary metrics strictly from chronological event facts.
        """
        if not history.events:
            raise ValueError("Cannot derive metrics from an empty history.")

        created_at = history.events[0].timestamp
        started_at = None
        completed_at = None
        failed_at = None
        outcome = "PENDING"
        failure_reason = None

        for event in history.events:
            if event.event_type == RenderEventType.JOB_CREATED:
                created_at = event.timestamp
            elif event.event_type == RenderEventType.STARTED:
                started_at = event.timestamp
            elif event.event_type == RenderEventType.COMPLETED:
                completed_at = event.timestamp
                outcome = "COMPLETED"
            elif event.event_type == RenderEventType.FAILED:
                failed_at = event.timestamp
                outcome = "FAILED"
                failure_reason = event.metadata.get("reason") or event.message
            elif event.event_type == RenderEventType.CANCELLED:
                completed_at = event.timestamp
                outcome = "CANCELLED"
                failure_reason = event.metadata.get("reason") or event.message

        duration_seconds = None
        if started_at:
            end_time = completed_at or failed_at
            if end_time:
                duration_seconds = (end_time - started_at).total_seconds()

        return cls(
            job_id=history.job_id,
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            failed_at=failed_at,
            duration_seconds=duration_seconds,
            outcome=outcome,
            failure_reason=failure_reason
        )
