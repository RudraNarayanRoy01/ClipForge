from dataclasses import dataclass
from typing import Tuple, FrozenSet
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from .resolution_metadata import ResolutionMetadata
from .resolution_statistics import ResolutionStatistics

@dataclass(frozen=True)
class ResolutionSnapshot:
    """
    Immutable point-in-time observation of a Runtime Resolution.
    
    Detached from live objects. Contains no mutable references.
    """
    ordered_components: Tuple[str, ...]
    dependency_ordering: Tuple[FrozenSet[str], ...]
    metadata: ResolutionMetadata
    statistics: ResolutionStatistics
