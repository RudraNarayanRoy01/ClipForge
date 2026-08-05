from dataclasses import dataclass
from typing import Tuple
from datetime import datetime
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from backend.src.runtime.dependency.runtime_dependency import RuntimeDependency
from .composition_metadata import CompositionMetadata

@dataclass(frozen=True)
class CompositionSnapshot:
    """
    Immutable point-in-time Runtime Composition.
    """
    components: Tuple[RuntimeComponent, ...]
    dependencies: Tuple[RuntimeDependency, ...]
    metadata: CompositionMetadata
    timestamp: datetime
