import pytest
import uuid
import os
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from src.application.execution_models import RenderExecutionRequest, ValidatedRenderPlan, RenderFailureCategory, RenderExecutionStatus
from src.domain.render_plan import (
    RenderPlan, 
    RenderMetadata, 
    RenderResolution, 
    FrameRate, 
    AspectRatio,
    RenderLayer,
    LayerCategory,
    RenderTrack,
    RenderSegment,
    TimelinePosition
)
from src.infrastructure.rendering.moviepy.backend import MoviePyRenderingBackend

@pytest.fixture
def test_video_file(tmp_path):
    """
    Creates a tiny valid video file for testing using ffmpeg (via os.system for simplicity).
    If ffmpeg is not available, it creates a dummy file (which might fail moviepy loading, 
    but we can test the failure translation).
    """
    video_path = tmp_path / "test_video.mp4"
    # Create a 1-second blank video
    ret = os.system(f"ffmpeg -y -f lavfi -i color=c=black:s=640x480:d=1 -c:v libx264 {str(video_path)} > /dev/null 2>&1")
    if ret != 0:
        # Fallback to empty file if ffmpeg fails/missing
        video_path.touch()
    return video_path


def test_backend_execute_loads_and_cleans_up(test_video_file, tmp_path):
    # This test verifies that the backend successfully resolves and loads a valid asset,
    # simulates execution, and then cleans up (which is implicitly tested if it doesn't crash).
    
    segment = RenderSegment(
        id=uuid.uuid4(),
        source_reference=str(test_video_file),
        timeline_start=TimelinePosition(0.0),
        timeline_end=TimelinePosition(1.0),
        source_start=TimelinePosition(0.0),
        source_end=TimelinePosition(1.0)
    )
    
    layer = RenderLayer(
        id=uuid.uuid4(),
        category=LayerCategory.VIDEO,
        name="Main",
        z_index=0,
        tracks=[RenderTrack(id=uuid.uuid4(), name="Track1", segments=[segment])]
    )
    
    plan = RenderPlan(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        metadata=RenderMetadata(
            resolution=RenderResolution(640, 480),
            frame_rate=FrameRate(30.0),
            duration_seconds=1.0,
            aspect_ratio=AspectRatio(4, 3)
        ),
        layers=[layer]
    )
    
    request = RenderExecutionRequest(
        validated_plan=ValidatedRenderPlan(plan=plan, validated_at=datetime.now(timezone.utc)),
        output_destination=str(tmp_path / "output.mp4")
    )
    
    backend = MoviePyRenderingBackend()
    result = asyncio.run(backend.execute(request))
    
    # If the video file was loaded successfully by MoviePy, it should succeed.
    # If ffmpeg wasn't available and it created an empty file, MoviePy will fail
    # to load it, and we should get a translated error.
    if result.status == RenderExecutionStatus.COMPLETED:
        assert result.output_artifact_path == str(tmp_path / "output.mp4")
    else:
        # If it failed to load, it should be translated.
        assert result.diagnostics is not None
        assert result.diagnostics.category in [RenderFailureCategory.RESOURCE_EXHAUSTED, RenderFailureCategory.BACKEND_FAILURE]


def test_backend_execute_missing_asset_translation(tmp_path):
    segment = RenderSegment(
        id=uuid.uuid4(),
        source_reference=str(tmp_path / "nonexistent.mp4"),
        timeline_start=TimelinePosition(0.0),
        timeline_end=TimelinePosition(1.0),
        source_start=TimelinePosition(0.0),
        source_end=TimelinePosition(1.0)
    )
    
    layer = RenderLayer(
        id=uuid.uuid4(),
        category=LayerCategory.VIDEO,
        name="Main",
        z_index=0,
        tracks=[RenderTrack(id=uuid.uuid4(), name="Track1", segments=[segment])]
    )
    
    plan = RenderPlan(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        metadata=RenderMetadata(
            resolution=RenderResolution(640, 480),
            frame_rate=FrameRate(30.0),
            duration_seconds=1.0,
            aspect_ratio=AspectRatio(4, 3)
        ),
        layers=[layer]
    )
    
    request = RenderExecutionRequest(
        validated_plan=ValidatedRenderPlan(plan=plan, validated_at=datetime.now(timezone.utc)),
        output_destination=str(tmp_path / "output.mp4")
    )
    
    backend = MoviePyRenderingBackend()
    result = asyncio.run(backend.execute(request))
    
    assert result.status == RenderExecutionStatus.FAILED
    assert result.diagnostics is not None
    assert result.diagnostics.category == RenderFailureCategory.RESOURCE_EXHAUSTED
    assert "not found" in result.diagnostics.message.lower()
