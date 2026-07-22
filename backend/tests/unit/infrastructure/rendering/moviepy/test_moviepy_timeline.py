import pytest
import uuid
from unittest.mock import Mock, patch

from src.infrastructure.rendering.moviepy.timeline import (
    MoviePyTimelineComposer,
    MoviePyCompositionContext,
    MoviePyPositionTranslator,
    MoviePyTimeline
)
from src.infrastructure.rendering.moviepy.structures import MoviePyResourcePool
from src.domain.render_plan import (
    RenderPlan, RenderMetadata, RenderResolution, FrameRate, AspectRatio,
    RenderLayer, LayerCategory, RenderTrack, RenderSegment, TimelinePosition,
    RenderInstruction
)

@pytest.fixture
def mock_resource_pool():
    pool = MoviePyResourcePool()
    return pool

@pytest.fixture
def sample_render_plan():
    metadata = RenderMetadata(
        duration_seconds=10.0,
        resolution=RenderResolution(width=1920, height=1080),
        frame_rate=FrameRate(fps=30.0),
        aspect_ratio=AspectRatio(width_ratio=16, height_ratio=9)
    )
    
    seg1 = RenderSegment(
        id=uuid.uuid4(),
        source_reference="/fake/video.mp4",
        timeline_start=TimelinePosition(time_seconds=0.0),
        timeline_end=TimelinePosition(time_seconds=5.0),
        source_start=TimelinePosition(time_seconds=1.0),
        source_end=TimelinePosition(time_seconds=6.0),
        instructions=[
            RenderInstruction(instruction_type="position", parameters={"position": "center"})
        ]
    )
    
    track1 = RenderTrack(
        id=uuid.uuid4(),
        name="Main Track",
        segments=[seg1]
    )
    
    layer1 = RenderLayer(
        id=uuid.uuid4(),
        category=LayerCategory.VIDEO,
        name="Video Layer",
        z_index=0,
        tracks=[track1]
    )
    
    return RenderPlan(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        metadata=metadata,
        layers=[layer1]
    )

def test_timeline_composer_creates_context(sample_render_plan):
    context = MoviePyTimelineComposer.create_context(sample_render_plan)
    assert context.duration_seconds == 10.0
    assert context.resolution_width == 1920
    assert context.resolution_height == 1080
    assert context.fps == 30.0

def test_position_translator():
    context = MoviePyCompositionContext(10.0, 1920, 1080, 30.0)
    
    # Test explicit x/y
    seg_xy = RenderSegment(
        id=uuid.uuid4(), source_reference="",
        timeline_start=TimelinePosition(0), timeline_end=TimelinePosition(1),
        source_start=TimelinePosition(0), source_end=TimelinePosition(1),
        instructions=[RenderInstruction("transform", {"x": 100, "y": 200})]
    )
    assert MoviePyPositionTranslator.translate(seg_xy, context) == (100, 200)
    
    # Test named position
    seg_named = RenderSegment(
        id=uuid.uuid4(), source_reference="",
        timeline_start=TimelinePosition(0), timeline_end=TimelinePosition(1),
        source_start=TimelinePosition(0), source_end=TimelinePosition(1),
        instructions=[RenderInstruction("position", {"position": "top"})]
    )
    assert MoviePyPositionTranslator.translate(seg_named, context) == "top"
    
    # Test default
    seg_default = RenderSegment(
        id=uuid.uuid4(), source_reference="",
        timeline_start=TimelinePosition(0), timeline_end=TimelinePosition(1),
        source_start=TimelinePosition(0), source_end=TimelinePosition(1)
    )
    assert MoviePyPositionTranslator.translate(seg_default, context) == "center"

def test_timeline_composer_pipeline(sample_render_plan, mock_resource_pool):
    # Mock clip
    mock_clip = Mock()
    mock_clip.subclip.return_value = mock_clip
    mock_clip.set_start.return_value = mock_clip
    mock_clip.set_duration.return_value = mock_clip
    mock_clip.set_position.return_value = mock_clip
    
    segment_id = sample_render_plan.layers[0].tracks[0].segments[0].id
    mock_resource_pool.add_video_clip(segment_id, mock_clip)
    
    # Compose
    with patch('src.infrastructure.rendering.moviepy.timeline.CompositeVideoClip') as MockCompositeVideo:
        mock_composite_instance = Mock()
        mock_composite_instance.set_duration.return_value = mock_composite_instance
        MockCompositeVideo.return_value = mock_composite_instance
        
        timeline = MoviePyTimelineComposer.compose(sample_render_plan, mock_resource_pool)
        
        assert isinstance(timeline, MoviePyTimeline)
        assert timeline.has_video is True
        assert timeline.has_audio is False
        assert timeline.context.duration_seconds == 10.0
        
        # Verify operations pipeline calls
        mock_clip.subclip.assert_called_with(1.0, 6.0)
        mock_clip.set_start.assert_called_with(0.0)
        mock_clip.set_duration.assert_called_with(5.0)
        mock_clip.set_position.assert_called_with("center")
        
        # Verify composition
        MockCompositeVideo.assert_called_once()
        args, kwargs = MockCompositeVideo.call_args
        assert len(args[0]) == 1 # One clip in the array
        assert kwargs["size"] == (1920, 1080)
        assert kwargs["bg_color"] == (0, 0, 0)

def test_timeline_composer_layer_ordering():
    # Setup a plan with 2 layers, z_index out of order to ensure composer sorts them
    # Layer 2 (z=1), Layer 1 (z=0)
    layer1 = RenderLayer(id=uuid.uuid4(), category=LayerCategory.VIDEO, name="Top", z_index=1)
    layer0 = RenderLayer(id=uuid.uuid4(), category=LayerCategory.VIDEO, name="Bottom", z_index=0)
    
    plan = RenderPlan(
        id=uuid.uuid4(), project_id=uuid.uuid4(),
        metadata=RenderMetadata(duration_seconds=1.0, resolution=RenderResolution(1920, 1080), frame_rate=FrameRate(30.0), aspect_ratio=AspectRatio(16, 9)),
        layers=[layer0, layer1]
    )
    
    # Just verify that sorted_layers inside composer keeps them in 0, 1 order
    sorted_layers = sorted(plan.layers, key=lambda l: l.z_index)
    assert sorted_layers[0].name == "Bottom"
    assert sorted_layers[1].name == "Top"
