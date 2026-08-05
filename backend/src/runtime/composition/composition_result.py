from dataclasses import dataclass
from typing import Tuple, Optional
from .runtime_composition import RuntimeComposition

@dataclass(frozen=True)
class CompositionResult:
    """
    Result of a Runtime Composition build process.
    Immutable.
    """
    success: bool
    composition: Optional[RuntimeComposition]
    warnings: Tuple[str, ...]
    errors: Tuple[str, ...]
