"""
Computes Service Statistics.
"""
from typing import Sequence
from .runtime_service import RuntimeService
from .service_statistics import ServiceStatistics

class ServiceStatisticsBuilder:
    """Pure computation of structural metrics for services."""
    
    @staticmethod
    def build(services: Sequence[RuntimeService]) -> ServiceStatistics:
        total = len(services)
        singletons = sum(1 for s in services if s.lifetime.upper() == "SINGLETON")
        transients = sum(1 for s in services if s.lifetime.upper() == "TRANSIENT")
        scoped = sum(1 for s in services if s.lifetime.upper() == "SCOPED")
        deps = sum(len(s.dependencies) for s in services)
        grouped = len(set(s.service_type for s in services))
        
        return ServiceStatistics(
            total_services=total,
            singleton_services=singletons,
            transient_services=transients,
            scoped_services=scoped,
            dependency_count=deps,
            grouped_services=grouped
        )
