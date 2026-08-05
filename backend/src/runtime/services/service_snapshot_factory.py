"""
Creates service snapshots.
"""
from typing import Sequence
from .runtime_service import RuntimeService
from .service_metadata import ServiceMetadata
from .service_statistics import ServiceStatistics
from .service_snapshot import ServiceSnapshot

class ServiceSnapshotFactory:
    """Creates immutable snapshots of the service composition."""
    
    @staticmethod
    def create(
        composition_id: str,
        services: Sequence[RuntimeService],
        metadata: ServiceMetadata,
        statistics: ServiceStatistics
    ) -> ServiceSnapshot:
        return ServiceSnapshot(
            composition_id=composition_id,
            services=tuple(services),
            metadata=metadata,
            statistics=statistics
        )
