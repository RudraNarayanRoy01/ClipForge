from typing import Tuple
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from backend.src.runtime.dependency.runtime_dependency import RuntimeDependency
from .composition_metadata import CompositionMetadata
from .composition_snapshot import CompositionSnapshot

class CompositionSnapshotFactory:
    """
    Factory for constructing immutable CompositionSnapshots.
    
    Responsibilities:
    - Construct immutable snapshots
    - Preserve deterministic ordering
    - Preserve timestamps
    - Preserve metadata
    """
    
    @staticmethod
    def create(
        components: Tuple[RuntimeComponent, ...],
        dependencies: Tuple[RuntimeDependency, ...],
        metadata: CompositionMetadata
    ) -> CompositionSnapshot:
        """
        Constructs a point-in-time snapshot.
        Preserves ordering inherent in the provided tuples.
        """
        return CompositionSnapshot(
            components=components,
            dependencies=dependencies,
            metadata=metadata,
            timestamp=metadata.creation_timestamp
        )
