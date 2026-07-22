import uuid
from enum import Enum, auto
from dataclasses import dataclass, replace
from typing import Optional
from datetime import datetime, timezone

class InvalidStateTransitionError(Exception):
    """Raised when an invalid lifecycle state transition is attempted."""
    pass


@dataclass(frozen=True)
class RenderExecutionId:
    """Immutable identifier for a render execution."""
    value: str

    @classmethod
    def generate(cls) -> "RenderExecutionId":
        return cls(value=str(uuid.uuid4()))


class RenderExecutionState(Enum):
    """Typed states of a render execution lifecycle."""
    QUEUED = auto()
    STARTING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass(frozen=True)
class RenderExecutionMetadata:
    """Immutable metadata snapshot of a render execution lifecycle."""
    id: RenderExecutionId
    state: RenderExecutionState
    creation_time: datetime
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None

    @property
    def elapsed_duration_seconds(self) -> Optional[float]:
        """Calculates elapsed duration if started. Returns total duration if finished."""
        if not self.start_time:
            return None
            
        end_time = self.completion_time or datetime.now(timezone.utc)
        return (end_time - self.start_time).total_seconds()


class RenderExecutionLifecycle:
    """
    Manages the strict, deterministic execution state of a rendering process.
    Produces immutable metadata snapshots on state transitions.
    Never invokes backends, schedules work, or orchestrates diagnostics.
    """
    
    def __init__(self, execution_id: Optional[RenderExecutionId] = None):
        """Initializes a new lifecycle, strictly entering the QUEUED state."""
        self._metadata = RenderExecutionMetadata(
            id=execution_id or RenderExecutionId.generate(),
            state=RenderExecutionState.QUEUED,
            creation_time=datetime.now(timezone.utc)
        )

    @property
    def metadata(self) -> RenderExecutionMetadata:
        """Exposes the current immutable metadata snapshot."""
        return self._metadata

    @property
    def is_terminal(self) -> bool:
        """Returns True if the lifecycle has reached a terminal state."""
        return self._metadata.state in {
            RenderExecutionState.COMPLETED, 
            RenderExecutionState.FAILED, 
            RenderExecutionState.CANCELLED
        }

    def _transition_to(self, new_state: RenderExecutionState, **kwargs) -> RenderExecutionMetadata:
        """Internal helper for applying strict state transitions."""
        if self.is_terminal:
            raise InvalidStateTransitionError(
                f"Cannot transition to {new_state.name} from terminal state {self._metadata.state.name}."
            )
        
        self._metadata = replace(self._metadata, state=new_state, **kwargs)
        return self._metadata

    def transition_to_starting(self) -> RenderExecutionMetadata:
        """Transitions from QUEUED to STARTING."""
        if self._metadata.state != RenderExecutionState.QUEUED:
            raise InvalidStateTransitionError(
                f"Cannot transition to STARTING from {self._metadata.state.name}."
            )
        return self._transition_to(RenderExecutionState.STARTING)

    def transition_to_running(self) -> RenderExecutionMetadata:
        """Transitions from STARTING to RUNNING, recording the start time."""
        if self._metadata.state != RenderExecutionState.STARTING:
            raise InvalidStateTransitionError(
                f"Cannot transition to RUNNING from {self._metadata.state.name}."
            )
        return self._transition_to(
            RenderExecutionState.RUNNING, 
            start_time=datetime.now(timezone.utc)
        )

    def transition_to_completed(self) -> RenderExecutionMetadata:
        """Transitions from RUNNING to COMPLETED, recording the completion time."""
        if self._metadata.state != RenderExecutionState.RUNNING:
            raise InvalidStateTransitionError(
                f"Cannot transition to COMPLETED from {self._metadata.state.name}."
            )
        return self._transition_to(
            RenderExecutionState.COMPLETED, 
            completion_time=datetime.now(timezone.utc)
        )

    def transition_to_failed(self) -> RenderExecutionMetadata:
        """Transitions to FAILED from STARTING or RUNNING."""
        if self._metadata.state not in {RenderExecutionState.STARTING, RenderExecutionState.RUNNING}:
            raise InvalidStateTransitionError(
                f"Cannot transition to FAILED from {self._metadata.state.name}."
            )
        return self._transition_to(
            RenderExecutionState.FAILED, 
            completion_time=datetime.now(timezone.utc)
        )

    def transition_to_cancelled(self) -> RenderExecutionMetadata:
        """Transitions to CANCELLED from any non-terminal state."""
        if self.is_terminal:
            raise InvalidStateTransitionError(
                f"Cannot transition to CANCELLED from terminal state {self._metadata.state.name}."
            )
        
        return self._transition_to(
            RenderExecutionState.CANCELLED,
            completion_time=datetime.now(timezone.utc)
        )
