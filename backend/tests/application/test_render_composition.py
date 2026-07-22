import pytest
import uuid
from src.application.render_composition_service import RenderCompositionService
from src.editing.domain.models.state import TimelineState, TimelineMetadata, TimelineTrack
from src.editing.domain.enums.tracks import TimelineTrackType
from src.editing.domain.models.items import Clip, Subtitle, Overlay
from src.editing.domain.enums.items import TimelineItemType, ScalingMode
from src.editing.domain.value_objects.time import Time, TimeRange
from src.editing.domain.value_objects.spatial import BoundingBox, Position, Size
from src.domain.models.render_profile import RenderProfile
from src.domain.entities import Resolution
from src.domain.value_objects import AspectRatio
from src.domain.render_plan import LayerCategory
from src.domain.models.render_draft import RenderDraft

def create_dummy_data():
    metadata = TimelineMetadata(fps=30.0, resolution=(1920, 1080), sample_rate=44100)
    total_duration = Time(value=10.0)
    
    # Clip 1 (starts at 5.0)
    clip1 = Clip(
        id=uuid.uuid4(),
        item_type=TimelineItemType.CLIP,
        timeline_time_range=TimeRange(start=Time(value=5.0), end=Time(value=10.0)),
        asset_id=uuid.uuid4(),
    )
    
    # Clip 2 (starts at 0.0) - Should be sorted first
    clip2 = Clip(
        id=uuid.uuid4(),
        item_type=TimelineItemType.CLIP,
        timeline_time_range=TimeRange(start=Time(value=0.0), end=Time(value=5.0)),
        asset_id=uuid.uuid4(),
    )
    
    video_track = TimelineTrack(
        id=uuid.uuid4(),
        track_type=TimelineTrackType.VIDEO,
        items=(clip1, clip2)
    )
    
    timeline_state = TimelineState(
        video_tracks=(video_track,),
        audio_tracks=(),
        overlay_tracks=(),
        subtitle_tracks=(),
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
    
    return timeline_state, render_profile


def test_composition_is_deterministic():
    timeline_state, render_profile = create_dummy_data()
    draft = RenderDraft(timeline_state=timeline_state, render_profile=render_profile)
    
    service = RenderCompositionService()
    plan1 = service.compose(draft)
    plan2 = service.compose(draft)
    
    # Check deterministic layer ordering
    assert [layer.category for layer in plan1.layers] == [
        LayerCategory.VIDEO,
        LayerCategory.AUDIO,
        LayerCategory.OVERLAY,
        LayerCategory.SUBTITLE
    ]
    
    # Check deterministic segment sorting within a track
    video_layer = plan1.layers[0]
    track = video_layer.tracks[0]
    assert track.segments[0].timeline_start.time_seconds == 0.0
    assert track.segments[1].timeline_start.time_seconds == 5.0
    
    # Test statelessness and idempotency (mostly):
    assert plan1.metadata.duration_seconds == plan2.metadata.duration_seconds
    assert plan1.metadata.resolution.width == plan2.metadata.resolution.width


def test_item_normalization():
    timeline_state, render_profile = create_dummy_data()
    draft = RenderDraft(timeline_state=timeline_state, render_profile=render_profile)
    service = RenderCompositionService()
    plan = service.compose(draft)
    
    video_layer = plan.layers[0]
    segment = video_layer.tracks[0].segments[0]
    
    # Verify instruction creation
    instruction_names = [i.instruction_type for i in segment.instructions]
    assert "playback_speed" in instruction_names
    assert "scaling" in instruction_names
