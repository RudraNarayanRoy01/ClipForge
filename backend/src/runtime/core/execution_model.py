from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional

from .runtime_planning import PlanningDecision
from .runtime_policy import PolicyDecision
from .runtime_constraint_engine import ConstraintDecision
from .runtime_budget_planner import BudgetDecision
from .runtime_routing import RoutingDecision


class ExecutionState(str, Enum):
    """
    Immutable Runtime execution states.
    """
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"


class ExecutionPriority(str, Enum):
    """
    Immutable Runtime execution priorities.
    """
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
    BACKGROUND = "BACKGROUND"


class ExecutionOutcome(str, Enum):
    """
    Architectural meaning of an execution result.
    """
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"


@dataclass(frozen=True)
class ExecutionIdentity:
    """
    The permanent identity of an execution.
    
    A pure identity value object. Must NOT contain distributed tracing 
    concerns (like correlation_id) or execution state.
    """
    execution_id: str
    created_at: float


@dataclass(frozen=True)
class ExecutionRequest:
    """
    Approved work waiting for execution.
    
    Owned by Runtime Execution Model.
    Consumed by RuntimeScheduler.
    
    Strictly declarative. Must NEVER contain ExecutionResult, scheduler info, 
    retry info, resource allocation, execution metrics, or transition logic.
    """
    identity: ExecutionIdentity
    planning_decision: Optional[PlanningDecision] = None
    policy_decision: Optional[PolicyDecision] = None
    constraint_decision: Optional[ConstraintDecision] = None
    budget_decision: Optional[BudgetDecision] = None
    routing_decision: Optional[RoutingDecision] = None
    request_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionStatus:
    """
    A snapshot of execution state metadata.
    
    Owned by Runtime Execution Model.
    Produced by RuntimeExecutor.
    Consumed by Observation.
    
    Does NOT own lifecycle.
    Does NOT perform transitions.
    Does NOT validate transitions.
    Does NOT calculate progress.
    """
    identity: ExecutionIdentity
    state: ExecutionState
    progress: float
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    last_updated_at: Optional[float] = None
    duration: Optional[float] = None
    status_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionResult:
    """
    Represents "What happened".
    
    Owned by Runtime Execution Model.
    Produced by RuntimeExecutor.
    Consumed by Retry, Observation, Learning, Optimization.
    
    Must NEVER contain retry decisions, scheduling decisions, optimization hints, 
    or recovery strategies. Never drives architecture.
    """
    identity: ExecutionIdentity
    outcome: ExecutionOutcome
    duration: float
    output_summary: Dict[str, Any] = field(default_factory=dict)
    failure_summary: Optional[Dict[str, Any]] = None
    resource_usage_summary: Dict[str, Any] = field(default_factory=dict)
    result_metadata: Dict[str, Any] = field(default_factory=dict)
