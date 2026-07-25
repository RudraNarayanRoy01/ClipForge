from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any

from .execution_model import ExecutionIdentity


class LifecycleState(str, Enum):
    """
    Immutable Runtime execution lifecycle states.
    
    Represents only the state of the execution lifecycle.
    Does NOT represent ExecutionStatus, Retry status, or Observation state.
    """
    CREATED = "CREATED"
    INITIALIZED = "INITIALIZED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TERMINATED = "TERMINATED"


class LifecycleStage(str, Enum):
    """
    Immutable Runtime lifecycle stages.
    
    Represents the major phase of the runtime lifecycle.
    Separate from LifecycleState.
    """
    EXECUTION = "EXECUTION"
    POST_EXECUTION = "POST_EXECUTION"
    FINALIZED = "FINALIZED"


@dataclass(frozen=True)
class LifecycleIdentity:
    """
    The permanent identity of a lifecycle progression.
    
    A pure identity value object. Must NOT contain execution state.
    """
    lifecycle_id: str
    created_at: float


@dataclass(frozen=True)
class LifecycleSummary:
    """
    Immutable lifecycle summary information.
    
    Must NOT contain Metrics, Telemetry, Retry history, or Execution behavior.
    """
    summary: str
    reason: str
    transition_count: int = 0
    warnings: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class LifecycleTransition:
    """
    The canonical immutable representation of Runtime state transitions.
    
    Consumed by Retry, Observation, Learning, Optimization.
    Must remain strictly immutable and free of behavioral logic.
    """
    previous_state: LifecycleState
    current_state: LifecycleState
    transition_reason: str
    timestamp: float


@dataclass(frozen=True)
class LifecycleResult:
    """
    The immutable outcome of Runtime lifecycle progression.
    
    Produced by RuntimeLifecycle.
    Consumed by Retry, Observation, Learning, Optimization.
    
    Must NEVER contain Execution logic, Scheduling information, Retry decisions,
    Observation information, Telemetry, Metrics, Monitoring, or Resource allocation.
    """
    lifecycle_identity: LifecycleIdentity
    execution_identity: ExecutionIdentity
    state: LifecycleState
    stage: LifecycleStage
    summary: LifecycleSummary
    transitions: List[LifecycleTransition] = field(default_factory=list)
    started_at: float = 0.0
    updated_at: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
