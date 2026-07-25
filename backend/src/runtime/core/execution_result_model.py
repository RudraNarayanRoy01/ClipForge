from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .execution_model import ExecutionIdentity
    from .scheduling_model import SchedulingIdentity


class ExecutionStatus(str, Enum):
    """
    Immutable Runtime execution state.
    
    Represents only Runtime execution state.
    Does NOT represent Scheduling, Lifecycle, Retry, or Observation.
    """
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ExecutionOutcome(str, Enum):
    """
    The final business outcome of Runtime execution.
    
    Represents the business outcome (e.g. SUCCESS, FAILURE).
    Separate from ExecutionStatus, which represents execution state.
    """
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class ExecutionSummary:
    """
    Immutable execution information.
    
    Does NOT contain Metrics, Telemetry, Retry history, or Lifecycle information.
    """
    summary: str
    reason: str
    completed_steps: int = 0
    failed_steps: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionResult:
    """
    The immutable outcome of Runtime execution.
    
    Produced by RuntimeExecutor.
    Consumed by Lifecycle, Retry, Observation, Learning, Optimization.
    
    Must NEVER contain Retry information, Lifecycle state, Resource allocation,
    Telemetry, Metrics, Monitoring, or Optimization state.
    """
    execution_identity: ExecutionIdentity
    scheduling_identity: SchedulingIdentity
    status: ExecutionStatus
    outcome: ExecutionOutcome
    summary: ExecutionSummary
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    duration: Optional[float] = None
    result_metadata: Dict[str, Any] = field(default_factory=dict)
