"""
Injection Result.

Immutable Runtime boundary for injection foundation construction.
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple

from .runtime_injection_composition import RuntimeInjectionComposition


@dataclass(frozen=True)
class InjectionResult:
    """
    Immutable result of an injection composition build operation.
    """
    success: bool
    composition: Optional[RuntimeInjectionComposition] = None
    errors: Tuple[str, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)
