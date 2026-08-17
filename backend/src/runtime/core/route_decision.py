from dataclasses import dataclass
from typing import Optional

from .policy_decision import PolicyDecision


@dataclass(frozen=True)
class RouteDecision:
    """
    Immutable representation of the Runtime's abstract routing boundary.

    This contract answers: "Given an approved policy decision, what
    abstract execution class should this workload be routed toward?"

    It establishes the boundary immediately downstream of Policy, preventing
    routing from silently bypassing the policy gate. It does NOT contain
    provider, model, hardware, or scheduling identities.
    """
    policy_decision: PolicyDecision
    execution_class: str
    is_routed: bool
    fallback_allowed: bool
