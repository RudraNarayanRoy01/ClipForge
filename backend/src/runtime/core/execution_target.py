from dataclasses import dataclass
from typing import Optional

from .route_decision import RouteDecision


@dataclass(frozen=True)
class TargetDescription:
    """
    Immutable description of an available execution target.
    
    This is strictly descriptive data about an available infrastructure destination.
    It does NOT contain executable objects, provider implementations, or hardware allocations.
    """
    target_id: str
    target_class: str  # local, remote, balanced, etc.
    provider: str
    model: Optional[str] = None
    compute_class: Optional[str] = None


@dataclass(frozen=True)
class ExecutionTarget:
    """
    Immutable representation of the concrete execution target selected for a route.
    
    This contract answers: "Which available concrete target satisfies the 
    abstract route class?"
    
    It is declarative and provider/model/hardware neutral.
    It MUST NOT contain:
    - executable objects
    - scheduling queue handlers
    - execution handles
    - provider client SDKs
    """
    route_decision: RouteDecision
    target_id: str
    target_class: str
    provider: str
    model: Optional[str] = None
    compute_class: Optional[str] = None
