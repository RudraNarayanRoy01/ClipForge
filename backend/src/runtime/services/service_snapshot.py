"""
Service snapshot representation.
"""
from dataclasses import dataclass
from typing import Tuple
from .runtime_service import RuntimeService
from .service_metadata import ServiceMetadata
from .service_statistics import ServiceStatistics

@dataclass(frozen=True)
class ServiceSnapshot:
    """Immutable point-in-time snapshot of the Service Composition."""
    composition_id: str
    services: Tuple[RuntimeService, ...]
    metadata: ServiceMetadata
    statistics: ServiceStatistics
