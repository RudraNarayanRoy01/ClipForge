from dataclasses import dataclass, replace
from typing import Optional

from src.application.rendering.models import (
    RenderJob,
    RenderProgress,
    RenderCancellationToken,
)
from src.application.rendering.telemetry import (
    RenderExecutionHistory,
    RenderExecutionMetrics,
    RenderExecutionEvent,
)


@dataclass(frozen=True)
class RenderExecutionSession:
    """
    The application's primary execution read model and composition boundary.
    This session unifies job metadata, execution history, progress, and cancellation.
    
    Future queues, workers, APIs, dashboards, and distributed rendering components 
    should integrate through this session abstraction rather than assembling individual 
    progress, cancellation, or telemetry models themselves.

    Instances of this class are strictly immutable. Every state transition yields a new instance.
    """
    job: RenderJob
    history: RenderExecutionHistory
    cancellation_token: RenderCancellationToken
    progress: Optional[RenderProgress] = None

    @classmethod
    def initialize(cls, job: RenderJob) -> "RenderExecutionSession":
        """
        Creates an initial session for a given job.
        """
        return cls(
            job=job,
            history=RenderExecutionHistory(job_id=job.id),
            cancellation_token=RenderCancellationToken(job_id=job.id),
            progress=None
        )

    @property
    def metrics(self) -> RenderExecutionMetrics:
        """Dynamically derives metrics from the execution history."""
        # Note: If history is empty, from_history will raise ValueError, 
        # so we only call it if we have at least one event.
        if not self.history.events:
            # Return a default pending metrics if no events yet
            from datetime import datetime
            return RenderExecutionMetrics(
                job_id=self.job.id,
                created_at=datetime.utcnow()
            )
        return RenderExecutionMetrics.from_history(self.history)

    def with_job(self, job: RenderJob) -> "RenderExecutionSession":
        """Returns a new session with an updated job."""
        return replace(self, job=job)

    def with_event(self, event: RenderExecutionEvent) -> "RenderExecutionSession":
        """Returns a new session with the event recorded in its history."""
        new_history = self.history.record_event(event)
        return replace(self, history=new_history)

    def with_progress(self, progress: RenderProgress) -> "RenderExecutionSession":
        """Returns a new session with updated progress."""
        return replace(self, progress=progress)

    def with_cancellation(self) -> "RenderExecutionSession":
        """Returns a new session with cancellation requested."""
        new_token = self.cancellation_token.request_cancellation()
        return replace(self, cancellation_token=new_token)
