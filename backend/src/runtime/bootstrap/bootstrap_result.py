from dataclasses import dataclass, field
from typing import Dict, Any, List
from .runtime_state import RuntimeState


@dataclass(frozen=True)
class BootstrapResult:
    """
    Immutable result object representing the final outcome of the bootstrap process.
    Contains no Runtime references.
    """
    success: bool
    runtime_state: RuntimeState
    duration: float
    warnings: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)
    initialized_components: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
