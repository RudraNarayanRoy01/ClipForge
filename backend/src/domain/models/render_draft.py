from dataclasses import dataclass

from src.editing.domain.models.state import TimelineState
from src.domain.models.render_profile import RenderProfile


@dataclass(frozen=True)
class RenderDraft:
    """
    Intermediate rendering specification representing the assembled inputs 
    required for rendering.
    
    Contains assembled rendering information only, remaining backend independent
    and completely decoupled from filesystem locations or execution context.
    """
    timeline_state: TimelineState
    render_profile: RenderProfile
