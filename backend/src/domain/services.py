from typing import Protocol

from src.domain.models.rendering import RenderSettings, RenderResult
from src.domain.models.export import ExportRequest, ExportResult
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

class IExportProvider(Protocol):
    """
    Defines the technology-agnostic export capability for ClipForge.
    Responsible for executing an export operation based on an ExportRequest.
    Maintains complete backend independence by relying solely on domain models.
    """
    def export(self, request: ExportRequest) -> ExportResult:
        """
        Executes an export operation based on the provided request.
        
        Args:
            request: The complete configuration and source details for the export.
            
        Returns:
            ExportResult: The outcome of the export operation.
            
        Raises:
            Exception: Implementations should propagate infrastructure failures naturally.
        """
        ...
