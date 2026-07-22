import pytest
import uuid
import tempfile
import os
from unittest.mock import patch

from src.application.render_planner import RenderPlanner
from src.application.render_validator import RenderValidator
from src.application.render_composition_service import RenderCompositionService
from src.application.render_planning_pipeline import RenderPlanningPipeline
from src.application.execution_models import ValidatedRenderPlan, RenderExecutionStatus, RenderExecutionResult

# Replace RenderExecutionPipeline and RenderExecutor with the new execution service
from src.application.render_execution_service import RenderExecutionService

from src.infrastructure.rendering.moviepy.backend import MoviePyRenderingBackend
from src.domain.render_plan import RenderPlan
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
    Verifies that TimelineState -> RenderPlanningPipeline -> RenderPlan -> RenderExecutionService -> Backend -> RenderExecutionResult
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
    
    backend = MoviePyRenderingBackend()
    execution_service = RenderExecutionService(backend=backend)
    
    # 3. Execute Planning Phase
    # TimelineState -> RenderPlanningPipeline -> RenderPlan
    render_plan = planning_pipeline.execute(timeline_state, render_profile)
    
    assert isinstance(render_plan, RenderPlan)
    assert len(render_plan.layers) == 4
    assert render_plan.metadata.duration_seconds == total_duration.value
    
    # Wrap in ValidatedRenderPlan (normally done by the pipeline/service layer before handing to execution service)
    # The RenderExecutionService requires a ValidatedRenderPlan
    import datetime
    validated_plan = ValidatedRenderPlan(plan=render_plan, validated_at=datetime.datetime.utcnow())
    
    # 4. Execute Rendering Phase (with the MoviePy backend skeleton)
    temp_dir = tempfile.gettempdir()
    dummy_result_path = os.path.join(temp_dir, "test_render.mp4")
    
    # The new skeleton always returns a success result immediately, without throwing exceptions,
    # thereby verifying the architectural integrity of the pipeline end-to-end.
    import asyncio
    result = asyncio.run(execution_service.execute_plan(validated_plan, dummy_result_path))
    
    # Verify result is successfully obtained and no abstraction was bypassed
    assert isinstance(result, RenderExecutionResult)
    assert result.status == RenderExecutionStatus.COMPLETED
    assert result.output_artifact_path == dummy_result_path

