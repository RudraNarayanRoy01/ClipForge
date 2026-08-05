from dataclasses import dataclass
from typing import Tuple
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from backend.src.runtime.dependency.runtime_dependency import RuntimeDependency
from .composition_metadata import CompositionMetadata
from .composition_statistics import CompositionStatistics
from .composition_snapshot import CompositionSnapshot

@dataclass(frozen=True)
class RuntimeComposition:
    """
    The canonical assembled Runtime representation.
    Nothing executes. Nothing initializes.
    """
    composition_id: str
    components: Tuple[RuntimeComponent, ...]
    dependencies: Tuple[RuntimeDependency, ...]
    metadata: CompositionMetadata
    statistics: CompositionStatistics

    def get_snapshot(self) -> CompositionSnapshot:
        """Returns a point-in-time snapshot of the runtime composition."""
        from .composition_snapshot_factory import CompositionSnapshotFactory
        return CompositionSnapshotFactory.create(
            components=self.components,
            dependencies=self.dependencies,
            metadata=self.metadata
        )
