import time
from typing import Optional

from src.domain.contracts.render_backend import IRenderBackend
from src.application.execution_models import (
    RenderExecutionRequest, 
    RenderExecutionResult,
)
from src.infrastructure.rendering.moviepy.translation import MoviePyRequestTranslator
from src.infrastructure.rendering.moviepy.exceptions import MoviePyExceptionTranslator
from src.infrastructure.rendering.moviepy.loader import MoviePyAssetLoader
from src.infrastructure.rendering.moviepy.timeline import MoviePyTimelineComposer


class MoviePyRenderingBackend(IRenderBackend):
    """
    Concrete implementation of IRenderBackend using MoviePy.
    
    Responsible for executing a RenderExecutionRequest using MoviePy constructs.
    It remains stateless and translates all backend failures to ensure
    MoviePy exceptions never escape the Infrastructure layer.
    """

    def __init__(self, translator: Optional[MoviePyRequestTranslator] = None):
        """
        Initializes the MoviePyRenderingBackend.
        
        Args:
            translator: Utility to translate the application request into backend state.
        """
        self._translator = translator or MoviePyRequestTranslator()

    async def execute(self, request: RenderExecutionRequest) -> RenderExecutionResult:
        """
        Executes a rendering request asynchronously.
        
        Args:
            request (RenderExecutionRequest): The execution request containing a validated RenderPlan.
            
        Returns:
            RenderExecutionResult: The outcome of the rendering process, including neutral 
                                   status and diagnostics, abstracting away backend-specific errors.
        """
        start_time = time.monotonic()
        moviepy_task = None
        
        try:
            # 1. Translate backend-agnostic request to MoviePy-specific task structure
            moviepy_task = self._translator.translate(
                request.validated_plan, 
                request.output_destination
            )
            
            # 2. Resource loading and validation
            # The loader securely resolves references into backend-owned resources.
            # Ownership remains isolated inside the task's ResourcePool.
            MoviePyAssetLoader.load_assets(
                request.validated_plan.plan, 
                moviepy_task.resources
            )
            
            # 3. Timeline Composition
            # Compose the timeline, yielding a detached immutable composition graph
            # Note: No export or encoding is performed in this batch.
            timeline = MoviePyTimelineComposer.compose(
                plan=request.validated_plan.plan, 
                resources=moviepy_task.resources
            )
            
            # (Export deferred to Batch 5.5.5.4: Output Composition)
            duration = time.monotonic() - start_time
            return RenderExecutionResult.success(
                duration_seconds=duration,
                output_artifact_path=request.output_destination
            )
            
        except Exception as e:
            # 4. Explicit Exception Translation
            # Ensure exceptions never escape the Infrastructure layer.
            category, message, details = MoviePyExceptionTranslator.translate(e)
            
            duration = time.monotonic() - start_time
            return RenderExecutionResult.failure(
                duration_seconds=duration,
                category=category,
                message=message,
                details=details
            )
            
        finally:
            # 5. Deterministic Cleanup
            # Driven purely by ownership logic, independent of execution success/failure.
            if moviepy_task is not None:
                moviepy_task.resources.cleanup()
