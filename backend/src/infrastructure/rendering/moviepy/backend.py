import time
from typing import Optional

from src.domain.ports import IRenderBackend
from src.domain.render_plan import RenderPlan
from src.domain.models.render_result import RenderResult, RenderStatus
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

    async def execute(self, plan: RenderPlan, output_path: str) -> RenderResult:
        """
        Orchestrates rendering asynchronously by delegating to the executor.
        """
        start_time = time.monotonic()
        moviepy_task = None
        
        try:
            # 1. Translate backend-agnostic plan to MoviePy-specific task structure
            moviepy_task = self._translator.translate(
                plan, 
                output_path
            )
            
            # 2. Resource loading
            MoviePyAssetLoader.load_assets(
                plan, 
                moviepy_task.resources
            )
            
            # 3. Timeline Composition
            timeline = MoviePyTimelineComposer.compose(
                plan=plan, 
                resources=moviepy_task.resources
            )
            
            # 4. Output Composition (Specification)
            render_output = MoviePyOutputComposer.compose_output(
                timeline=timeline,
                custom_metadata=None # Passing None or generic metadata
            )
            
            # 5. Prepare Execution Context
            context = MoviePyExecutionContext(
                execution_destination=output_path,
                resource_pool=moviepy_task.resources,
                runtime_options={}
            )
            
            # 6. Execute Render (Executor handles its own exceptions and cleanup)
            execution_result = MoviePyRenderExecutor.execute(render_output, context)
            
            # 7. Translate Execution Result to Domain Result
            if execution_result.success:
                return RenderResult(
                    status=RenderStatus.COMPLETED,
                    rendered_output_location=output_path,
                    rendered_duration=execution_result.elapsed_time_seconds
                )
            else:
                return RenderResult(
                    status=RenderStatus.FAILED,
                    message=execution_result.failure_message,
                    rendering_metadata=execution_result.diagnostics
                )
            
        except Exception as e:
            # Catch exceptions that occur BEFORE execution (e.g., during translation, loading, composition)
            category, message, details = MoviePyExceptionTranslator.translate(e)
            
            return RenderResult(
                status=RenderStatus.FAILED,
                message=message,
                rendering_metadata=details
            )
            
        finally:
            # Deterministic Fallback Cleanup (e.g., if exception occurred before executor)
            if moviepy_task is not None:
                moviepy_task.resources.cleanup()
