import os
import uuid
import pytest
from pathlib import Path

from src.infrastructure.rendering.moviepy.execution import (
    MoviePyExecutionContext,
    MoviePyRenderExecutor
)
from src.infrastructure.rendering.moviepy.structures import MoviePyResourcePool
from src.infrastructure.rendering.moviepy.output import MoviePyRenderOutput, MoviePyRenderConfiguration
from src.infrastructure.rendering.moviepy.timeline import MoviePyTimeline, MoviePyCompositionContext

try:
    from moviepy.editor import ColorClip
except ImportError:
    ColorClip = None

@pytest.fixture
def temp_output_dir(tmp_path):
    output_dir = tmp_path / "integration_render_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

@pytest.mark.integration
def test_end_to_end_execution_success(temp_output_dir):
    """Verifies that MoviePyRenderExecutor can actually render a real file to disk."""
    if ColorClip is None:
        pytest.skip("MoviePy is not installed or not working properly.")
        
    output_path = temp_output_dir / "test_render.mp4"
    
    # 1. Setup minimal timeline with a ColorClip
    context = MoviePyCompositionContext(
        duration_seconds=1.0,
        resolution_width=640,
        resolution_height=360,
        fps=10.0
    )
    
    # A simple 1-second red video
    clip = ColorClip(size=(640, 360), color=(255, 0, 0), duration=1.0)
    
    timeline = MoviePyTimeline(
        context=context,
        _root_video=clip,
        _root_audio=None
    )
    
    config = MoviePyRenderConfiguration(
        fps=10.0,
        resolution=(640, 360)
    )
    
    render_output = MoviePyRenderOutput(
        id=uuid.uuid4(),
        timeline=timeline,
        configuration=config,
        metadata={"test": "integration"}
    )
    
    resource_pool = MoviePyResourcePool()
    
    exec_context = MoviePyExecutionContext(
        execution_destination=str(output_path),
        resource_pool=resource_pool,
        runtime_options={"codec": "libx264"}
    )
    
    # 2. Execute Render
    result = MoviePyRenderExecutor.execute(render_output, exec_context)
    
    # 3. Assertions
    assert result.success is True
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert result.elapsed_time_seconds > 0
    
    # Check that cleanup doesn't fail
    assert "cleanup_error_type" not in result.output_metadata


@pytest.mark.integration
def test_execution_handles_invalid_destination(temp_output_dir):
    """Verifies that rendering to an invalid path is caught and translated."""
    if ColorClip is None:
        pytest.skip("MoviePy is not installed.")
        
    # An invalid path on Windows/Linux
    output_path = "/invalid/directory/path/that/does/not/exist/test_render.mp4"
    if os.name == 'nt':
        output_path = "Z:\\invalid\\directory\\path\\test_render.mp4"
    
    context = MoviePyCompositionContext(
        duration_seconds=1.0,
        resolution_width=640,
        resolution_height=360,
        fps=10.0
    )
    clip = ColorClip(size=(640, 360), color=(0, 255, 0), duration=1.0)
    
    timeline = MoviePyTimeline(
        context=context,
        _root_video=clip,
        _root_audio=None
    )
    
    config = MoviePyRenderConfiguration(
        fps=10.0,
        resolution=(640, 360)
    )
    
    render_output = MoviePyRenderOutput(
        id=uuid.uuid4(),
        timeline=timeline,
        configuration=config
    )
    
    resource_pool = MoviePyResourcePool()
    # Add a mock resource to verify cleanup
    class MockResource:
        closed = False
        def close(self):
            self.closed = True
            
    mock_resource = MockResource()
    resource_pool.add_video_clip(uuid.uuid4(), mock_resource)
    
    exec_context = MoviePyExecutionContext(
        execution_destination=str(output_path),
        resource_pool=resource_pool,
        runtime_options={"codec": "libx264"}
    )
    
    result = MoviePyRenderExecutor.execute(render_output, exec_context)
    
    # Assertions
    assert result.success is False
    assert result.failure_category is not None
    assert result.failure_message is not None
    
    # Cleanup should still have occurred
    assert mock_resource.closed is True
