from src.application.rendering_pipeline import RenderingPipeline
from src.domain.models.rendering import RenderSettings, RenderResult
from src.editing.domain.models.state import TimelineState


class RenderingBackend:
    """
    Public application-facing façade for the rendering subsystem.
    
    Exposes rendering capabilities to the rest of ClipForge while delegating
    all orchestration and execution details to the RenderingPipeline. 
    It serves as the single entry point for rendering.
    """

    def __init__(self, pipeline: RenderingPipeline):
        """
        Initializes the RenderingBackend.
        
        Args:
            pipeline: The RenderingPipeline responsible for coordinating rendering requests.
        """
        self._pipeline = pipeline

    def render(self, timeline_state: TimelineState, render_settings: RenderSettings) -> RenderResult:
        """
        Executes a rendering request.
        
        Delegates the rendering execution to the underlying RenderingPipeline. Any failures
        are allowed to propagate naturally without introducing retry or recovery logic.
        
        Args:
            timeline_state: The state of the timeline to render.
            render_settings: The configuration for the rendering process.
            
        Returns:
            RenderResult: The result of the rendering process.
        """
        return self._pipeline.execute(timeline_state, render_settings)
