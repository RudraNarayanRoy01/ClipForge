from abc import ABC, abstractmethod

from src.application.execution_models import RenderExecutionRequest, RenderExecutionResult

class IRenderBackend(ABC):
    """
    Contract for rendering backends.
    This interface defines the required capabilities of a rendering infrastructure
    without exposing its implementation details, keeping the Application layer
    renderer-agnostic.
    """

    @abstractmethod
    async def execute(self, request: RenderExecutionRequest) -> RenderExecutionResult:
        """
        Executes a rendering request asynchronously.
        
        Args:
            request (RenderExecutionRequest): The execution request containing a validated RenderPlan.
            
        Returns:
            RenderExecutionResult: The outcome of the rendering process, including neutral 
                                   status and diagnostics, abstracting away backend-specific errors.
        """
        pass
