from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional

from .runtime_planning import PlanningDecision
from .runtime_policy import PolicyDecision
from .runtime_constraint_engine import ConstraintDecision
from .runtime_budget_planner import BudgetDecision
from .runtime_routing import RoutingDecision


class ExecutionPriority(str, Enum):
    """
    Immutable Runtime execution priorities.
    """
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
    BACKGROUND = "BACKGROUND"


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
