import pytest
import uuid
import os
import tempfile
import asyncio
from datetime import datetime

# Skip if moviepy is not installed or ffmpeg not found
pytest.importorskip("moviepy")

from src.infrastructure.rendering.moviepy.loader import MoviePyAssetLoader
from src.infrastructure.rendering.moviepy.timeline import MoviePyTimelineComposer, MoviePyTimeline
from src.infrastructure.rendering.moviepy.structures import MoviePyResourcePool, MoviePyRenderTask
from src.infrastructure.rendering.moviepy.backend import MoviePyRenderingBackend
from src.domain.render_plan import (
    RenderPlan, RenderMetadata, RenderResolution, FrameRate, AspectRatio,
    RenderLayer, LayerCategory, RenderTrack, RenderSegment, TimelinePosition, RenderInstruction
)
from src.application.execution_models import RenderExecutionRequest, ValidatedRenderPlan, RenderExecutionStatus

@pytest.fixture
def temp_video_file():
    # We create a tiny valid video file or mock one if possible. 
    # Since we can't easily generate an mp4 here reliably without moviepy,
    # we'll use a ColorClip from moviepy and write it, then use it as source.
    from moviepy.editor import ColorClip
    clip = ColorClip(size=(640, 480), color=(255, 0, 0), duration=2.0)
    
    fd, path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    
    clip.write_videofile(path, fps=24, logger=None)
    clip.close()
    
    yield path
    
    if os.path.exists(path):
        os.remove(path)

@pytest.fixture
def integration_render_plan(temp_video_file):
    metadata = RenderMetadata(
        duration_seconds=5.0,
        resolution=RenderResolution(width=1280, height=720),
        frame_rate=FrameRate(fps=30.0),
        aspect_ratio=AspectRatio(width_ratio=16, height_ratio=9)
    )
    
    seg = RenderSegment(
        id=uuid.uuid4(),
        source_reference=temp_video_file,
        timeline_start=TimelinePosition(time_seconds=1.0),
        timeline_end=TimelinePosition(time_seconds=3.0),
        source_start=TimelinePosition(time_seconds=0.0),
        source_end=TimelinePosition(time_seconds=2.0),
        instructions=[RenderInstruction("position", {"x": 100, "y": 100})]
    )
    
    track = RenderTrack(id=uuid.uuid4(), name="Video Track", segments=[seg])
    layer = RenderLayer(id=uuid.uuid4(), category=LayerCategory.VIDEO, name="Video Layer", z_index=0, tracks=[track])
    
    return RenderPlan(id=uuid.uuid4(), project_id=uuid.uuid4(), metadata=metadata, layers=[layer])

def test_timeline_composition_integration_lifecycle(integration_render_plan):
    pool = MoviePyResourcePool()
    
    # 1. Load assets
    MoviePyAssetLoader.load_assets(integration_render_plan, pool)
    
    segment_id = integration_render_plan.layers[0].tracks[0].segments[0].id
    assert pool.get_video_clip(segment_id) is not None
    
    # 2. Compose
    timeline = MoviePyTimelineComposer.compose(integration_render_plan, pool)
    
    assert isinstance(timeline, MoviePyTimeline)
    assert timeline.context.duration_seconds == 5.0
    assert timeline.context.resolution_width == 1280
    assert timeline.has_video is True
    
    # MoviePy specifics: root_video should be a CompositeVideoClip
    from moviepy.editor import CompositeVideoClip
    assert isinstance(timeline._root_video, CompositeVideoClip)
    assert timeline._root_video.duration == 5.0
    
    # 3. Verify Ownership / Cleanup
    # Cleanup should close clips but not throw errors on the timeline structure itself
    pool.cleanup()
    
    assert pool.get_video_clip(segment_id) is None
    
@pytest.mark.asyncio
async def test_backend_execution_incorporates_composition(integration_render_plan):
    """
    Test that the backend execute method successfully orchestrates loading and composition
    and returns a success result without performing a file export.
    """
    validated = ValidatedRenderPlan(plan=integration_render_plan, validated_at=datetime.utcnow())
    request = RenderExecutionRequest(validated_plan=validated, output_destination="/tmp/never_written.mp4")
    
    backend = MoviePyRenderingBackend()
    result = await backend.execute(request)
    
    assert result.status == RenderExecutionStatus.COMPLETED
    assert result.output_artifact_path == "/tmp/never_written.mp4"
    assert not os.path.exists("/tmp/never_written.mp4")
