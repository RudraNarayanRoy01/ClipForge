import uuid
from typing import List

from src.domain.render_plan import (
    RenderPlan,
    RenderMetadata,
    RenderLayer,
    RenderTrack,
    LayerCategory
)


class RenderPlanBuilder:
    """
    Builder for assembling an immutable RenderPlan deterministically.
    
    This builder is restricted to construction responsibilities only. It does not
    contain business logic or depend on editing domain models. It accepts normalized
    rendering data and produces a completely immutable aggregate root.
    """

    def __init__(self, project_id: uuid.UUID, metadata: RenderMetadata):
        self._project_id = project_id
        self._metadata = metadata
        self._layers: List[RenderLayer] = []

    def add_layer(self, category: LayerCategory, name: str, z_index: int, tracks: List[RenderTrack]) -> 'RenderPlanBuilder':
        """
        Adds a complete rendering layer.
        
        Args:
            category: The type of media layer (VIDEO, AUDIO, etc.).
            name: Human-readable identifier.
            z_index: Deterministic rendering order (lower is rendered first).
            tracks: The deterministically ordered tracks within this layer.
            
        Returns:
            The builder instance.
        """
        layer = RenderLayer(
            id=uuid.uuid4(),
            category=category,
            name=name,
            z_index=z_index,
            tracks=tracks
        )
        self._layers.append(layer)
        return self

    def build(self) -> RenderPlan:
        """
        Assembles the final immutable RenderPlan.
        
        Layers are sorted by z_index to guarantee deterministic layer ordering.
        
        Returns:
            RenderPlan: The complete immutable execution blueprint.
        """
        # Ensure deterministic layer ordering based on z_index
        sorted_layers = sorted(self._layers, key=lambda l: l.z_index)

        return RenderPlan(
            id=uuid.uuid4(),
            project_id=self._project_id,
            metadata=self._metadata,
            layers=sorted_layers
        )
