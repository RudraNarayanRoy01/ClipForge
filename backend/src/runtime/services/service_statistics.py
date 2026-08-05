"""
Service statistics representation.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class ServiceStatistics:
    """Immutable statistics for a Service Composition."""
    total_services: int
    singleton_services: int
    transient_services: int
    scoped_services: int
    dependency_count: int
    grouped_services: int
