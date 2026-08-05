from dataclasses import dataclass, field
from typing import Optional, Tuple
from .runtime_component import RuntimeComponent

@dataclass(frozen=True)
class ComponentRegistrationResult:
    """
    Immutable result of a component registration attempt.
    """
    success: bool
    registered_component: Optional[RuntimeComponent] = None
    reason: str = ""
    warnings: Tuple[str, ...] = field(default_factory=tuple)
