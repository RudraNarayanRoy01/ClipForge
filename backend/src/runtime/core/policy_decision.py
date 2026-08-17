from dataclasses import dataclass, field
from typing import Tuple

from .planning_result import PlanningResult


@dataclass(frozen=True)
class PolicyDecision:
    """
    Immutable representation of the Runtime's policy evaluation decision.

    This contract answers: "Is this abstract planning approach acceptable
    under the Runtime's currently represented declarative policy?"

    It establishes the boundary between Planning and subsequent
    Routing/Scheduling/Execution layers. It explicitly does not contain
    provider, hardware, or scheduling logic.
    """
    planning_result: PlanningResult
    is_approved: bool
    policy_mode: str
    fallback_allowed: bool
    constraints: Tuple[str, ...] = field(default_factory=tuple)
