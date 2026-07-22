import uuid
import pytest
from unittest.mock import Mock, patch

from src.application.execution_models import RenderFailureCategory
from src.infrastructure.rendering.moviepy.execution import (
    MoviePyExecutionContext,
    MoviePyExecutionResult,
    MoviePyExecutionExceptionTranslator,
    MoviePyRenderExecutor
)
from src.infrastructure.rendering.moviepy.structures import MoviePyResourcePool
from src.infrastructure.rendering.moviepy.output import MoviePyRenderOutput, MoviePyRenderConfiguration
from src.infrastructure.rendering.moviepy.timeline import MoviePyTimeline, MoviePyCompositionContext

@pytest.fixture
def mock_resource_pool():
    pool = Mock(spec=MoviePyResourcePool)
    return pool

@pytest.fixture
def mock_context(mock_resource_pool):
    return MoviePyExecutionContext(
        execution_destination="/fake/path.mp4",
        resource_pool=mock_resource_pool,
        runtime_options={"codec": "libx264"}
    )

@pytest.fixture
def mock_timeline():
    context = MoviePyCompositionContext(
        duration_seconds=10.0,
        resolution_width=1920,
        resolution_height=1080,
        fps=30.0
    )
    mock_video = Mock()
    mock_audio = Mock()
    # set_audio should return a new mock representing the combined clip
    mock_combined = Mock()
    mock_video.set_audio.return_value = mock_combined
    
    return MoviePyTimeline(
        context=context,
        _root_video=mock_video,
        _root_audio=mock_audio
    )

@pytest.fixture
def mock_render_output(mock_timeline):
    config = MoviePyRenderConfiguration(
        fps=30.0,
        resolution=(1920, 1080)
    )
    return MoviePyRenderOutput(
        id=uuid.uuid4(),
        timeline=mock_timeline,
        configuration=config,
        metadata={"custom": "data"}
    )

def test_execution_success(mock_render_output, mock_context):
    result = MoviePyRenderExecutor.execute(mock_render_output, mock_context)
    
    # Verify execution result
    assert result.success is True
    assert result.elapsed_time_seconds >= 0
    assert result.output_metadata["custom"] == "data"
    
    # Verify lifecycle steps
    mock_video = mock_render_output.timeline._root_video
    mock_audio = mock_render_output.timeline._root_audio
    mock_combined = mock_video.set_audio.return_value
    
    # Ensure set_audio was called
    mock_video.set_audio.assert_called_once_with(mock_audio)
    
    # Ensure write_videofile was called on the combined clip
    mock_combined.write_videofile.assert_called_once_with(
        filename="/fake/path.mp4",
        fps=30.0,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
        logger=None
    )
    
    # Ensure cleanup was called
    mock_context.resource_pool.cleanup.assert_called_once()


def test_execution_audio_only(mock_render_output, mock_context):
    audio_timeline = MoviePyTimeline(
        context=mock_render_output.timeline.context,
        _root_video=None,
        _root_audio=Mock()
    )
    mock_render_output = MoviePyRenderOutput(
        id=mock_render_output.id,
        timeline=audio_timeline,
        configuration=mock_render_output.configuration,
        metadata=mock_render_output.metadata
    )
    
    result = MoviePyRenderExecutor.execute(mock_render_output, mock_context)
    
    assert result.success is True
    
    # Ensure write_audiofile was called on the audio clip
    mock_audio = mock_render_output.timeline._root_audio
    mock_audio.write_audiofile.assert_called_once()
    mock_context.resource_pool.cleanup.assert_called_once()


def test_execution_failure_translates_exceptions(mock_render_output, mock_context):
    # Mock an IOError during write_videofile
    mock_combined = mock_render_output.timeline._root_video.set_audio.return_value
    mock_combined.write_videofile.side_effect = IOError("Disk full")
    
    result = MoviePyRenderExecutor.execute(mock_render_output, mock_context)
    
    assert result.success is False
    assert result.failure_category == RenderFailureCategory.RESOURCE_EXHAUSTED
    assert "IO or OS error" in result.failure_message
    assert result.diagnostics["error_type"] == "OSError"
    assert "Disk full" in result.diagnostics["error_message"]
    
    # Ensure cleanup STILL gets called despite exception
    mock_context.resource_pool.cleanup.assert_called_once()


def test_execution_cleanup_failure_is_attached_to_diagnostics(mock_render_output, mock_context):
    # Mock a successful render, but cleanup fails
    mock_context.resource_pool.cleanup.side_effect = Exception("Failed to close handles")
    
    result = MoviePyRenderExecutor.execute(mock_render_output, mock_context)
    
    # The render itself succeeded, the exception in cleanup is caught and logged
    # Wait, the prompt says "Cleanup failures must never overwrite or hide the original rendering failure.
    # Preserve the primary execution exception and suppress or attach cleanup failures as diagnostics."
    # If rendering succeeds but cleanup fails, does it fail the whole task or just log it?
    # Our implementation attaches it to diagnostics and returns success if render was successful.
    
    assert result.success is True
    assert result.output_metadata["cleanup_error_type"] == "Exception"
    assert "Failed to close handles" in result.output_metadata["cleanup_error_message"]


def test_execution_failure_with_cleanup_failure(mock_render_output, mock_context):
    # Mock a render failure AND a cleanup failure
    mock_combined = mock_render_output.timeline._root_video.set_audio.return_value
    mock_combined.write_videofile.side_effect = ValueError("Invalid codec")
    mock_context.resource_pool.cleanup.side_effect = Exception("Cleanup crash")
    
    result = MoviePyRenderExecutor.execute(mock_render_output, mock_context)
    
    # The original error must take precedence
    assert result.success is False
    assert result.failure_category == RenderFailureCategory.VALIDATION_REQUIRED
    assert result.diagnostics["error_type"] == "ValueError"
    assert "Invalid codec" in result.diagnostics["error_message"]
    
    # Cleanup error should be attached
    assert result.diagnostics["cleanup_error_type"] == "Exception"
    assert "Cleanup crash" in result.diagnostics["cleanup_error_message"]
