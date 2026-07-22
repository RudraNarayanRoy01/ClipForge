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
from src.infrastructure.rendering.moviepy.output import MoviePyOutputComposer
from src.infrastructure.rendering.moviepy.execution import (
    MoviePyExecutionContext,
    MoviePyRenderExecutor
)


class MoviePyRenderingBackend(IRenderBackend):
    """
    Concrete implementation of IRenderBackend using MoviePy.
    
    Responsible for orchestrating the preparation of the execution context
    and delegating the actual rendering execution to the MoviePyRenderExecutor.
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
        Orchestrates rendering asynchronously by delegating to the executor.
        """
        start_time = time.monotonic()
        moviepy_task = None
        
        try:
            # 1. Translate backend-agnostic request to MoviePy-specific task structure
            moviepy_task = self._translator.translate(
                request.validated_plan, 
                request.output_destination
            )
            
            # 2. Resource loading
            MoviePyAssetLoader.load_assets(
                request.validated_plan.plan, 
                moviepy_task.resources
            )
            
            # 3. Timeline Composition
            timeline = MoviePyTimelineComposer.compose(
                plan=request.validated_plan.plan, 
                resources=moviepy_task.resources
            )
            
            # 4. Output Composition (Specification)
            render_output = MoviePyOutputComposer.compose_output(
                timeline=timeline,
                custom_metadata=request.execution_options.get("metadata")
            )
            
            # 5. Prepare Execution Context
            context = MoviePyExecutionContext(
                execution_destination=request.output_destination,
                resource_pool=moviepy_task.resources,
                runtime_options=request.execution_options
            )
            
            # 6. Execute Render (Executor handles its own exceptions and cleanup)
            execution_result = MoviePyRenderExecutor.execute(render_output, context)
            
            # 7. Translate Execution Result
            if execution_result.success:
                return RenderExecutionResult.success(
                    duration_seconds=execution_result.elapsed_time_seconds,
                    output_artifact_path=request.output_destination
                )
            else:
                return RenderExecutionResult.failure(
                    duration_seconds=execution_result.elapsed_time_seconds,
                    category=execution_result.failure_category,
                    message=execution_result.failure_message,
                    details=execution_result.diagnostics
                )
            
        except Exception as e:
            # Catch exceptions that occur BEFORE execution (e.g., during translation, loading, composition)
            category, message, details = MoviePyExceptionTranslator.translate(e)
            
            duration = time.monotonic() - start_time
            return RenderExecutionResult.failure(
                duration_seconds=duration,
                category=category,
                message=message,
                details=details
            )
            
        finally:
            # Deterministic Fallback Cleanup (e.g., if exception occurred before executor)
            if moviepy_task is not None:
                moviepy_task.resources.cleanup()
