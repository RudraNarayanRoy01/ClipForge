from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any

from .lifecycle_model import LifecycleIdentity

class RetryDecision(str, Enum):
    """
    The immutable outcome of retry evaluation.
    
    Represents only "What should happen?".
    Does NOT contain behavior to execute, schedule, delay, queue, or cancel retry.
    Future Runtime components (e.g., Recovery Engine) interpret this decision.
    """
    RETRY = "RETRY"
    DO_NOT_RETRY = "DO_NOT_RETRY"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    ABORT = "ABORT"


class RetryReason(str, Enum):
    """
    The immutable reason why a retry decision was made.
    
    Separate from RetryDecision to preserve the distinction between 
    the decision outcome and the root cause evaluation.
    """
    TRANSIENT_FAILURE = "TRANSIENT_FAILURE"
    RESOURCE_UNAVAILABLE = "RESOURCE_UNAVAILABLE"
    TIMEOUT = "TIMEOUT"
    MODEL_FAILURE = "MODEL_FAILURE"
    VALIDATION_FAILURE = "VALIDATION_FAILURE"
    POLICY_LIMIT = "POLICY_LIMIT"
    SUCCESS_NO_RETRY = "SUCCESS_NO_RETRY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RetryPolicy:
    """
    Immutable representation of retry policy.
    
    Purely descriptive. It defines policy but does NOT implement it.
    Evaluated by RuntimeRetry. Future Recovery components implement the strategy.
    """
    maximum_attempts: int
    current_attempt: int
    retry_strategy: str
    retry_window: float


@dataclass(frozen=True)
class RetrySummary:
    """
    Immutable retry summary information.
    
    Contains descriptive outcomes of the retry evaluation.
    Must remain completely devoid of execution behavior, telemetry, or metrics.
    """
    summary: str
    reason: str
    remaining_attempts: int
    warnings: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RetryIdentity:
    """
    The permanent identity of a retry evaluation.
    
    A pure identity value object. Must NOT contain execution state.
    """
    retry_id: str
    created_at: float


@dataclass(frozen=True)
class RetryResult:
    """
    The immutable outcome of Runtime retry evaluation.
    
    Represents "What retry evaluation produced."
    Produced by RuntimeRetry.
    Consumed by Future Recovery and Observation components.
    
    Must NEVER contain Execution logic, Scheduling information, 
    Recovery behavior, Observation information, Learning information, 
    Optimization information, Telemetry, Metrics, Monitoring, 
    or Resource allocation.
    """
    retry_identity: RetryIdentity
    lifecycle_identity: LifecycleIdentity
    decision: RetryDecision
    reason: RetryReason
    policy: RetryPolicy
    summary: RetrySummary
    metadata: Dict[str, Any] = field(default_factory=dict)
