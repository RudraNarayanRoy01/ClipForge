"""
Result of building a Service Composition.
"""
from dataclasses import dataclass, field
from typing import Tuple, Optional
from .runtime_service_composition import RuntimeServiceComposition

@dataclass(frozen=True)
class ServiceResult:
    """Immutable Runtime boundary for Service Composition results."""
    success: bool
    service_composition: Optional[RuntimeServiceComposition] = None
    errors: Tuple[str, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)
