import pytest
import uuid
import tempfile
import os
from unittest.mock import patch

from src.application.render_planner import RenderPlanner
from src.application.render_validator import RenderValidator
from src.application.render_composition_service import RenderCompositionService
from src.application.render_planning_pipeline import RenderPlanningPipeline
from src.application.render_execution_pipeline import RenderExecutionPipeline
from src.application.render_executor import RenderExecutor
from src.infrastructure.rendering.moviepy_backend import MoviePyRenderingBackend
from src.domain.render_plan import RenderPlan
from src.domain.models.render_result import RenderResult, RenderStatus
from src.domain.models.render_profile import RenderProfile
from src.domain.entities import Resolution
from src.domain.value_objects import AspectRatio

from src.editing.domain.models.state import TimelineState, TimelineMetadata, TimelineTrack
from src.editing.domain.enums.tracks import TimelineTrackType
from src.editing.domain.models.items import Clip, Subtitle, Overlay
from src.editing.domain.enums.items import TimelineItemType, ScalingMode
from src.editing.domain.value_objects.time import Time, TimeRange
from src.editing.domain.value_objects.spatial import BoundingBox, Position, Size

def test_end_to_end_render_pipeline():
    """
    Verifies that TimelineState -> RenderPlanningPipeline -> RenderPlan -> RenderExecutionPipeline -> RenderExecutor -> Backend -> RenderResult
    operates as intended, without architectural leakage.
    """
    
    # 1. Setup the dummy dependencies and data
    metadata = TimelineMetadata(fps=30.0, resolution=(1920, 1080), sample_rate=44100)
    total_duration = Time(value=10.0)
    
    # Create a dummy video clip
    clip_id = uuid.uuid4()
    asset_id = uuid.uuid4()
    time_range = TimeRange(start=Time(value=0.0), end=Time(value=10.0))
    clip = Clip(
        id=clip_id,
        item_type=TimelineItemType.CLIP,
        timeline_time_range=time_range,
        asset_id=asset_id,
    )
    
    # Create a dummy subtitle
    subtitle = Subtitle(
        id=uuid.uuid4(),
        item_type=TimelineItemType.SUBTITLE,
        timeline_time_range=TimeRange(start=Time(value=1.0), end=Time(value=5.0)),
        text="Test Subtitle",
        position=Position(x=100, y=900)
    )
    
    # Create a dummy overlay
    overlay = Overlay(
        id=uuid.uuid4(),
        item_type=TimelineItemType.OVERLAY,
        timeline_time_range=TimeRange(start=Time(value=0.0), end=Time(value=10.0)),
        asset_id=uuid.uuid4(),
        bounding_box=BoundingBox(origin=Position(x=0, y=0), size=Size(width=200, height=200))
    )
    
    video_track = TimelineTrack(
        id=uuid.uuid4(),
        track_type=TimelineTrackType.VIDEO,
        items=(clip,)
    )
    
    subtitle_track = TimelineTrack(
        id=uuid.uuid4(),
        track_type=TimelineTrackType.SUBTITLE,
        items=(subtitle,)
    )
    
    overlay_track = TimelineTrack(
        id=uuid.uuid4(),
        track_type=TimelineTrackType.OVERLAY,
        items=(overlay,)
    )
    
    timeline_state = TimelineState(
        video_tracks=(video_track,),
        audio_tracks=(),
        overlay_tracks=(overlay_track,),
        subtitle_tracks=(subtitle_track,),
        metadata=metadata,
        total_duration=total_duration
    )
    
    render_profile = RenderProfile(
        name="1080p HD",
        profile_type="youtube",
        resolution=Resolution(width=1920, height=1080),
        aspect_ratio=AspectRatio.RATIO_16_9,
        frame_rate=30.0,
        video_codec="libx264",
        audio_codec="aac",
        video_bitrate="5000k",
        audio_bitrate="192k",
        sample_rate=44100,
        output_container=".mp4"
    )
    
    # 2. Build the Pipelines
    planner = RenderPlanner()
    validator = RenderValidator()
    composer = RenderCompositionService()
    
    planning_pipeline = RenderPlanningPipeline(
        planner=planner,
        validator=validator,
        composer=composer
    )
    
    # Use a dummy asset resolver
    def dummy_resolver(asset_id: uuid.UUID) -> str:
        return f"/dummy/path/{asset_id}.mp4"
    
    temp_dir = tempfile.gettempdir()
    backend = MoviePyRenderingBackend(asset_path_resolver=dummy_resolver, output_dir=temp_dir)
    executor = RenderExecutor(backend=backend)
    execution_pipeline = RenderExecutionPipeline(executor=executor)
    
    # 3. Execute Planning Phase
    # TimelineState -> RenderPlanningPipeline -> RenderPlan
    render_plan = planning_pipeline.execute(timeline_state, render_profile)
    
    assert isinstance(render_plan, RenderPlan)
    assert len(render_plan.layers) == 4
    assert render_plan.metadata.duration_seconds == total_duration.value
    
    # 4. Execute Rendering Phase (with mock moviepy)
    # RenderPlan -> RenderExecutionPipeline -> RenderResult
    
    # We patch the inner _execute_safe of MoviePyRenderingBackend just to simulate success 
    # without needing real video files, which guarantees architectural isolation is maintained.
    with patch.object(backend, '_execute_safe') as mock_execute_safe:
        dummy_result_path = os.path.join(temp_dir, "test_render.mp4")
        mock_execute_safe.return_value = RenderResult(
            status=RenderStatus.COMPLETED,
            rendered_output_location=dummy_result_path,
            rendered_duration=10.0,
            rendering_metadata={"provider": "MoviePyRenderingBackend"}
        )
        
        result = execution_pipeline.execute(render_plan)
        
        # Verify result is successfully obtained and no abstraction was bypassed
        assert isinstance(result, RenderResult)
        assert result.status == RenderStatus.COMPLETED
        assert result.rendered_output_location == dummy_result_path
        
        mock_execute_safe.assert_called_once_with(render_plan)

    # Alternatively, ensure it doesn't throw unexpected architectural errors if we actually run it
    real_result = execution_pipeline.execute(render_plan)
    assert isinstance(real_result, RenderResult)
    # The actual MoviePy execution should gracefully return FAILED because /dummy/path/ doesn't exist
    # or because moviepy is not installed. Either way, it must not throw, but return a RenderResult.
    assert real_result.status == RenderStatus.FAILED
    assert "MoviePyRenderingBackend" in real_result.rendering_metadata["provider"]
