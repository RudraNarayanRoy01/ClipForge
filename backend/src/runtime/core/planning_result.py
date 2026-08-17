from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from .intent import ExecutionIntent


@dataclass(frozen=True)
class PlanningResult:
    """
    Immutable representation of the Runtime's planning decision.

    This contract answers HOW the Runtime intends to satisfy
    an ExecutionIntent.

    It establishes the boundary between Planning and
    subsequent Policy/Routing/Scheduling stages.
    """
    intent: ExecutionIntent
    strategy: str
    requirements: Tuple[str, ...] = field(default_factory=tuple)
    constraints: Dict[str, Any] = field(default_factory=dict)
