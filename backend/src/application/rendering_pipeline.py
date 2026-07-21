from src.domain.services import IRenderingProvider
from src.domain.models.rendering import RenderSettings, RenderResult
from src.editing.domain.models.state import TimelineState


class RenderingPipeline:
    """
    Coordinates rendering requests for ClipForge.
    
    Acts purely as an orchestration layer between callers and rendering providers.
    It receives rendering requests, delegates the actual rendering to a technology-agnostic 
    provider, and returns the domain result, maintaining strict separation of concerns.
    """

    def __init__(self, provider: IRenderingProvider):
        """
        Initializes the RenderingPipeline with a specific rendering provider.
        
        Args:
            provider: The technology-agnostic rendering provider to delegate rendering to.
        """
        self._provider = provider

    def execute(self, timeline_state: TimelineState, render_settings: RenderSettings) -> RenderResult:
        """
        Coordinates a single rendering request.
        
        Delegates the execution to the underlying rendering provider, without introducing
        additional error handling, retry logic, or alternative providers.
        
        Args:
            timeline_state: The complete state of the timeline to be rendered.
            render_settings: The configuration specifying how rendering should occur.
            
        Returns:
            RenderResult: The outcome of the rendering request.
            
        Raises:
            Exception: Any exception raised by the provider propagates naturally.
        """
        return self._provider.render(timeline_state, render_settings)
