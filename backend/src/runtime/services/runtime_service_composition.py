"""
Runtime Service Composition artifact.
"""
from dataclasses import dataclass, field
from typing import Tuple, Mapping
from types import MappingProxyType
from .runtime_service import RuntimeService
from .service_metadata import ServiceMetadata
from .service_statistics import ServiceStatistics
from .service_snapshot import ServiceSnapshot

@dataclass(frozen=True)
class ValidationResult:
    """Immutable validation result for composition."""
    is_valid: bool
    errors: Tuple[str, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class RuntimeServiceComposition:
    """Canonical immutable Service Blueprint."""
    composition_id: str
    services: Tuple[RuntimeService, ...]
    metadata: ServiceMetadata
    statistics: ServiceStatistics
    validation_result: ValidationResult
    snapshot: ServiceSnapshot
    
    @property
    def service_map(self) -> Mapping[str, RuntimeService]:
        """Provides an immutable mapping of service_id to RuntimeService."""
        return MappingProxyType({s.service_id: s for s in self.services})
