import pytest
import uuid
from dataclasses import FrozenInstanceError
from src.domain.render_plan import (
    RenderPlan,
    RenderLayer,
    RenderTrack,
    RenderSegment,
    RenderInstruction,
    RenderMetadata,
    LayerCategory,
    RenderResolution,
    FrameRate,
    AspectRatio,
    TimelinePosition,
    SafeZone,
    RenderBounds,
    RenderTransform
)

def test_value_objects_validation():
    # RenderResolution
    with pytest.raises(ValueError):
        RenderResolution(width=0, height=1080)
    
    # FrameRate
    with pytest.raises(ValueError):
        FrameRate(fps=0)
    
    # AspectRatio
    with pytest.raises(ValueError):
        AspectRatio(width_ratio=16, height_ratio=0)
        
    # TimelinePosition
    with pytest.raises(ValueError):
        TimelinePosition(time_seconds=-1.0)
        
    # SafeZone
    with pytest.raises(ValueError):
        SafeZone(10, 10, -5, 10)
    with pytest.raises(ValueError):
        SafeZone(10, 10, 110, 10)

def test_render_segment_validation():
    source_ref = str(uuid.uuid4())
    # source end before source start
    with pytest.raises(ValueError):
        RenderSegment(
            id=uuid.uuid4(),
            source_reference=source_ref,
            timeline_start=TimelinePosition(0),
            timeline_end=TimelinePosition(10),
            source_start=TimelinePosition(10),
            source_end=TimelinePosition(5)
        )
    # timeline end before timeline start
    with pytest.raises(ValueError):
        RenderSegment(
            id=uuid.uuid4(),
            source_reference=source_ref,
            timeline_start=TimelinePosition(10),
            timeline_end=TimelinePosition(5),
            source_start=TimelinePosition(0),
            source_end=TimelinePosition(5)
        )

def test_render_track_validation():
    source_ref = str(uuid.uuid4())
    seg1 = RenderSegment(
        id=uuid.uuid4(),
        source_reference=source_ref,
        timeline_start=TimelinePosition(10),
        timeline_end=TimelinePosition(15),
        source_start=TimelinePosition(0),
        source_end=TimelinePosition(5)
    )
    seg2 = RenderSegment(
        id=uuid.uuid4(),
        source_reference=source_ref,
        timeline_start=TimelinePosition(5),  # Out of order
        timeline_end=TimelinePosition(10),
        source_start=TimelinePosition(0),
        source_end=TimelinePosition(5)
    )
    with pytest.raises(ValueError):
        RenderTrack(
            id=uuid.uuid4(),
            name="Video Track 1",
            segments=[seg1, seg2]
        )

def test_render_plan_validation():
    metadata = RenderMetadata(
        resolution=RenderResolution(1920, 1080),
        frame_rate=FrameRate(60.0),
        duration_seconds=15.0,
        aspect_ratio=AspectRatio(16, 9)
    )
    
    # Must have at least one layer
    with pytest.raises(ValueError):
        RenderPlan(
            id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            metadata=metadata,
            layers=[]
        )
        
    layer1 = RenderLayer(id=uuid.uuid4(), category=LayerCategory.VIDEO, name="BG", z_index=10)
    layer2 = RenderLayer(id=uuid.uuid4(), category=LayerCategory.OVERLAY, name="FG", z_index=5) # Out of order z_index
    
    # Layers must be ordered by z_index
    with pytest.raises(ValueError):
        RenderPlan(
            id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            metadata=metadata,
            layers=[layer1, layer2]
        )

def test_immutability():
    res = RenderResolution(width=1920, height=1080)
    with pytest.raises(FrozenInstanceError):
        res.width = 1280
        
    metadata = RenderMetadata(
        resolution=res,
        frame_rate=FrameRate(30.0),
        duration_seconds=10.0,
        aspect_ratio=AspectRatio(16, 9)
    )
    
    layer = RenderLayer(id=uuid.uuid4(), category=LayerCategory.VIDEO, name="BG", z_index=0)
    
    plan = RenderPlan(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        metadata=metadata,
        layers=[layer]
    )
    
    with pytest.raises(FrozenInstanceError):
        plan.layers = []
