import time
import contextlib
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from src.application.execution_models import RenderFailureCategory
from src.infrastructure.rendering.moviepy.output import MoviePyRenderOutput
from src.infrastructure.rendering.moviepy.structures import MoviePyResourcePool


@dataclass(frozen=True)
class MoviePyExecutionContext:
    """
    Encapsulates runtime-only state for execution.
    Contains destination paths, runtime options, timestamps, logging context,
    and the resource pool containing temporary execution state.
    """
    execution_destination: str
    resource_pool: MoviePyResourcePool
    runtime_options: Dict[str, Any] = field(default_factory=dict)
    logging_context: Dict[str, Any] = field(default_factory=dict)
    execution_start_time: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class MoviePyExecutionResult:
    """
    Immutable representation of the execution outcome.
    Exposes success, diagnostics, elapsed time, and output metadata.
    Never exposes MoviePy runtime objects.
    """
    success: bool
    elapsed_time_seconds: float
    output_metadata: Dict[str, Any] = field(default_factory=dict)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    failure_category: Optional[RenderFailureCategory] = None
    failure_message: Optional[str] = None

    @classmethod
    def create_success(cls, elapsed_time_seconds: float, metadata: Dict[str, Any]) -> 'MoviePyExecutionResult':
        return cls(
            success=True,
            elapsed_time_seconds=elapsed_time_seconds,
            output_metadata=metadata,
        )

    @classmethod
    def create_failure(
        cls, 
        elapsed_time_seconds: float, 
        category: RenderFailureCategory, 
        message: str, 
        diagnostics: Dict[str, Any]
    ) -> 'MoviePyExecutionResult':
        return cls(
            success=False,
            elapsed_time_seconds=elapsed_time_seconds,
            failure_category=category,
            failure_message=message,
            diagnostics=diagnostics
        )


class MoviePyExecutionExceptionTranslator:
    """
    Translates raw backend exceptions (MoviePy, FFmpeg, filesystem, etc.) 
    into backend-neutral execution diagnostics and failure categories.
    """
    
    @classmethod
    def translate(cls, exception: Exception) -> Tuple[RenderFailureCategory, str, Dict[str, Any]]:
        details: Dict[str, Any] = {
            "error_type": type(exception).__name__,
            "error_message": str(exception),
            "backend": "MoviePy"
        }
        
        if isinstance(exception, FileNotFoundError):
            category = RenderFailureCategory.RESOURCE_EXHAUSTED
            message = "Required asset not found on disk."
        elif isinstance(exception, PermissionError):
            category = RenderFailureCategory.RESOURCE_EXHAUSTED
            message = "Permission denied when accessing required asset or destination."
        elif isinstance(exception, ValueError):
            category = RenderFailureCategory.VALIDATION_REQUIRED
            message = "Invalid parameters or unsupported asset provided to the rendering backend."
        elif isinstance(exception, (OSError, IOError)):
            category = RenderFailureCategory.RESOURCE_EXHAUSTED
            message = "An IO or OS error occurred while executing render (e.g., FFmpeg failure, insufficient disk space)."
        else:
            category = RenderFailureCategory.BACKEND_FAILURE
            message = "An unexpected rendering execution error occurred."
            
        return category, message, details


class MoviePyRenderExecutor:
    """
    Orchestrates the execution of an immutable MoviePyRenderOutput into the final encoded media.
    Structured as a runtime lifecycle pipeline (prepare -> execute -> translate -> cleanup).
    Exception-safe and preserves dependency inversion.
    """

    @classmethod
    def execute(cls, output: MoviePyRenderOutput, context: MoviePyExecutionContext) -> MoviePyExecutionResult:
        """
        Main entry point for execution. Coordinates the runtime lifecycle safely.
        """
        start_time = time.monotonic()
        exception: Optional[Exception] = None
        cleanup_diagnostics: Dict[str, Any] = {}

        try:
            # 1. Prepare runtime state from immutable specification
            final_clip = cls._prepare_runtime(output)
            
            # 2. Execute render (wraps the MoviePy write_videofile operation)
            cls._execute_render(final_clip, output, context)
            
        except Exception as e:
            exception = e
            
        finally:
            # 3. Exception-safe cleanup
            cls._cleanup(context, cleanup_diagnostics)

        elapsed_time = time.monotonic() - start_time

        # 4. Produce immutable execution result
        return cls._produce_result(output, exception, elapsed_time, cleanup_diagnostics)

    @classmethod
    def _prepare_runtime(cls, output: MoviePyRenderOutput) -> Any:
        """
        Extracts and combines the audio and video tracks from the timeline.
        This does NOT mutate the timeline, but instead prepares a runtime-specific
        combination (like setting audio on the video clip) for rendering.
        """
        video = output.timeline._root_video
        audio = output.timeline._root_audio
        
        if video is not None and audio is not None:
            # MoviePy uses .set_audio to combine them for export
            # This returns a copy of the clip with the audio attached
            return video.set_audio(audio)
        elif video is not None:
            return video
        elif audio is not None:
            return audio
            
        raise ValueError("Timeline has neither video nor audio.")

    @classmethod
    def _execute_render(cls, final_clip: Any, output: MoviePyRenderOutput, context: MoviePyExecutionContext) -> None:
        """
        Wraps the raw MoviePy API calls to ensure the executor is responsible for orchestration
        rather than just exposing MoviePy APIs directly.
        """
        # Determine options based on configuration and runtime context
        options = context.runtime_options.copy()
        
        fps = output.configuration.fps
        
        # Audio-only rendering if no video
        if output.timeline._root_video is None and output.timeline._root_audio is not None:
            # MoviePy AudioClip write_audiofile
            final_clip.write_audiofile(
                filename=context.execution_destination,
                fps=options.get("audio_fps", 44100),
                logger=None  # Disable default MoviePy stdout logging
            )
        else:
            # Standard video rendering
            final_clip.write_videofile(
                filename=context.execution_destination,
                fps=fps,
                codec=options.get("codec", "libx264"),
                audio_codec=options.get("audio_codec", "aac"),
                preset=options.get("preset", "medium"),
                threads=options.get("threads", 4),
                logger=None  # Disable default MoviePy stdout logging
            )

    @classmethod
    def _cleanup(cls, context: MoviePyExecutionContext, diagnostics_out: Dict[str, Any]) -> None:
        """
        Ensures deterministic and exception-safe cleanup of the resource pool.
        Populates diagnostics_out with any cleanup failures to ensure they don't
        overwrite the primary execution failure.
        """
        try:
            context.resource_pool.cleanup()
        except Exception as e:
            # Cleanup failures must not bubble up and mask the original exception
            diagnostics_out["cleanup_error_type"] = type(e).__name__
            diagnostics_out["cleanup_error_message"] = str(e)

    @classmethod
    def _produce_result(
        cls, 
        output: MoviePyRenderOutput, 
        exception: Optional[Exception], 
        elapsed_time: float, 
        cleanup_diagnostics: Dict[str, Any]
    ) -> MoviePyExecutionResult:
        """
        Collects execution metadata and translates exceptions to produce an immutable result.
        """
        if exception:
            category, message, diagnostics = MoviePyExecutionExceptionTranslator.translate(exception)
            diagnostics.update(cleanup_diagnostics)
            return MoviePyExecutionResult.create_failure(
                elapsed_time_seconds=elapsed_time,
                category=category,
                message=message,
                diagnostics=diagnostics
            )
            
        metadata = output.metadata.copy()
        metadata.update(cleanup_diagnostics)
        return MoviePyExecutionResult.create_success(
            elapsed_time_seconds=elapsed_time,
            metadata=metadata
        )
