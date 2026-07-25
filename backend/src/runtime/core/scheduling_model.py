from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, Optional

from .execution_model import ExecutionIdentity


class SchedulingStatus(str, Enum):
    """
    Immutable Runtime scheduling statuses.
    Represents only scheduling outcomes, NOT execution outcomes.
    """
    READY = "READY"
    QUEUED = "QUEUED"
    DEFERRED = "DEFERRED"
    BLOCKED = "BLOCKED"
    REJECTED = "REJECTED"


class SchedulingPriority(str, Enum):
    """
    Immutable Runtime scheduling priorities.
    """
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
    BACKGROUND = "BACKGROUND"


class SchedulingPolicy(str, Enum):
    """
    Immutable Runtime scheduling policies (Business Rules).
    Defines HOW scheduling decisions are fundamentally governed.
    """
    IMMEDIATE = "IMMEDIATE"
    DEFERRED = "DEFERRED"
    BACKGROUND = "BACKGROUND"


class SchedulingStrategy(str, Enum):
    """
    Immutable Runtime scheduling strategies (Evaluation Methods).
    Defines HOW scheduling decisions are evaluated.
    """
    PRIORITY_FIRST = "PRIORITY_FIRST"
    ROUND_ROBIN = "ROUND_ROBIN"
    FIFO = "FIFO"
    WEIGHTED_PRIORITY = "WEIGHTED_PRIORITY"


class QueueClassification(str, Enum):
    """
    Purely declarative logical queue classification.
    Does NOT imply queue implementation, storage, or worker pools.
    """
    INTERACTIVE = "INTERACTIVE"
    BACKGROUND = "BACKGROUND"
    BATCH = "BATCH"
    HIGH_PRIORITY = "HIGH_PRIORITY"


@dataclass(frozen=True)
class SchedulingIdentity:
    """
    The permanent identity of a scheduling decision.
    
    A pure identity value object. Must NOT contain execution status,
    retry logic, lifecycle state, or resource allocation.
    """
    schedule_id: str
    created_at: float
    execution_identity: ExecutionIdentity


@dataclass(frozen=True)
class SchedulingDecision:
    """
    Immutable representation of an approved scheduling decision.
    
    Represents "What the scheduler decided", never "What actually executed".
    Owned by the RuntimeScheduler subsystem.
    Consumed by RuntimeExecutor and future Runtime subsystems.
    
    Must NEVER contain ExecutionResult, ExecutionStatus, Retry information,
    Lifecycle state, Resource allocation, Telemetry, or Metrics.
    """
    identity: SchedulingIdentity
    execution_identity: ExecutionIdentity
    status: SchedulingStatus
    priority: SchedulingPriority
    policy: SchedulingPolicy
    strategy: SchedulingStrategy
    queue_classification: QueueClassification
    scheduling_timestamp: float
    scheduling_reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)
