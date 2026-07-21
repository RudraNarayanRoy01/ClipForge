from typing import Protocol

from src.domain.models.rendering import RenderSettings, RenderResult
from src.editing.domain.models.state import TimelineState

class IRenderingProvider(Protocol):
    """
    Defines the canonical rendering capability for ClipForge.
    Responsible for rendering a TimelineState according to RenderSettings.
    Maintains complete backend independence by relying solely on domain models.
    """
    def render(self, timeline_state: TimelineState, render_settings: RenderSettings) -> RenderResult:
        """
        Renders a TimelineState using the specified RenderSettings.
        
        Args:
            timeline_state: The complete state of the timeline to be rendered.
            render_settings: The configuration specifying how rendering should occur.
            
        Returns:
            RenderResult: The outcome of the rendering request.
            
        Raises:
            Exception: Implementations should propagate rendering exceptions naturally.
        """
        ...
