from dataclasses import dataclass

from src.editing.domain.models.state import TimelineState
from src.domain.models.render_profile import RenderProfile


@dataclass(frozen=True)
class RenderPlan:
    """
    The canonical execution blueprint for rendering.
    
    Represents an immutable, validated set of instructions ready for the rendering pipeline.
    It contains no backend-specific state, execution threads, output paths, or external dependencies.
    """
    timeline_state: TimelineState
    render_profile: RenderProfile
