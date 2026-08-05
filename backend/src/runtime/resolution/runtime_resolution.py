from dataclasses import dataclass
from typing import Tuple, FrozenSet
from .resolution_metadata import ResolutionMetadata
from .resolution_statistics import ResolutionStatistics
from .resolution_snapshot import ResolutionSnapshot
from .resolution_validator import ResolutionValidationResult
from backend.src.runtime.registry.runtime_component import RuntimeComponent

@dataclass(frozen=True)
class RuntimeResolution:
    """
    Immutable dataclass representing the resolved dependency ordering.
    
    Determines the exact initialization ordering required by future Runtime execution.
    Computes ordering only, no execution.
    """
    resolution_id: str
    ordered_components: Tuple[RuntimeComponent, ...]
    dependency_order: Tuple[FrozenSet[str], ...]
    metadata: ResolutionMetadata
    statistics: ResolutionStatistics
    validation_result: ResolutionValidationResult

    def get_snapshot(self) -> ResolutionSnapshot:
        """Provide immutable snapshot generation without execution."""
        return ResolutionSnapshot(
            ordered_components=tuple(c.component_id for c in self.ordered_components),
            dependency_ordering=self.dependency_order,
            metadata=self.metadata,
            statistics=self.statistics
        )
