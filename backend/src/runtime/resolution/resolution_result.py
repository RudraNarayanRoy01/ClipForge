from dataclasses import dataclass, field
from typing import Tuple, Optional
from .runtime_resolution import RuntimeResolution

@dataclass(frozen=True)
class ResolutionResult:
    """
    Immutable result of the resolution orchestration.
    """
    success: bool
    resolution: Optional[RuntimeResolution] = None
    errors: Tuple[str, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)
