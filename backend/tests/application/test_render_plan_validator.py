import uuid
import pytest
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
    TimelinePosition,
    RenderInstruction
)
from src.application.validation.models import ValidationSeverity
from src.application.validation.render_plan_validator import RenderPlanValidator


@pytest.fixture
def valid_metadata():
    return RenderMetadata(
        resolution=RenderResolution(width=1920, height=1080),
        frame_rate=FrameRate(fps=30.0),
        duration_seconds=10.0,
        aspect_ratio=AspectRatio(width_ratio=16, height_ratio=9)
    )

@pytest.fixture
def valid_segment():
    return RenderSegment(
        id=uuid.uuid4(),
        source_reference="video.mp4",
        timeline_start=TimelinePosition(time_seconds=0.0),
        timeline_end=TimelinePosition(time_seconds=5.0),
        source_start=TimelinePosition(time_seconds=0.0),
        source_end=TimelinePosition(time_seconds=5.0),
        instructions=[
            RenderInstruction(instruction_type="crop", parameters={"x": 0, "y": 0, "w": 1920, "h": 1080})
        ]
    )

@pytest.fixture
def valid_track(valid_segment):
    return RenderTrack(
        id=uuid.uuid4(),
        name="Main Video",
        segments=[valid_segment]
    )

@pytest.fixture
def valid_layer(valid_track):
    return RenderLayer(
        id=uuid.uuid4(),
        category=LayerCategory.VIDEO,
        name="Video Layer 1",
        z_index=0,
        tracks=[valid_track]
    )

@pytest.fixture
def valid_plan(valid_metadata, valid_layer):
    return RenderPlan(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        metadata=valid_metadata,
        layers=[valid_layer]
    )


def test_validator_returns_success_for_valid_plan(valid_plan):
    validator = RenderPlanValidator()
    result = validator.validate(valid_plan)
    
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validator_detects_empty_layers(valid_plan):
    # Using object.__setattr__ to bypass dataclass frozen state for testing invalid states 
    # that might somehow be constructed or to simulate flawed aggregate roots.
    # Actually, RenderPlan's __post_init__ prevents empty layers. 
    # But if we bypass it:
    object.__setattr__(valid_plan, 'layers', [])
    
    validator = RenderPlanValidator()
    result = validator.validate(valid_plan)
    
    assert result.is_valid is False
    assert len(result.errors) == 1
    assert "no layers" in result.errors[0].message.lower()


def test_validator_warns_on_zero_duration(valid_metadata, valid_layer):
    object.__setattr__(valid_metadata, 'duration_seconds', 0.0)
    # Fix the segment so it doesn't extend beyond the 0 duration, which would cause an error
    segment = valid_layer.tracks[0].segments[0]
    object.__setattr__(segment.timeline_start, 'time_seconds', 0.0)
    object.__setattr__(segment.timeline_end, 'time_seconds', 0.0)
    plan = RenderPlan(id=uuid.uuid4(), project_id=uuid.uuid4(), metadata=valid_metadata, layers=[valid_layer])
    
    validator = RenderPlanValidator()
    result = validator.validate(plan)
    
    # 0 duration is a warning, not an error
    assert result.is_valid is True
    assert len(result.warnings) == 2
    assert any("duration is 0s" in w.message for w in result.warnings)


def test_validator_detects_invalid_metadata(valid_metadata, valid_layer):
    # Bypass post_init to test validator logic
    object.__setattr__(valid_metadata.resolution, 'width', 0)
    plan = RenderPlan(id=uuid.uuid4(), project_id=uuid.uuid4(), metadata=valid_metadata, layers=[valid_layer])
    
    validator = RenderPlanValidator()
    result = validator.validate(plan)
    
    assert result.is_valid is False
    assert any("resolution" in e.message.lower() for e in result.errors)


def test_validator_detects_empty_tracks(valid_layer, valid_plan):
    object.__setattr__(valid_layer, 'tracks', [])
    
    validator = RenderPlanValidator()
    result = validator.validate(valid_plan)
    
    # Info severity for empty tracks
    assert result.is_valid is True
    assert len(result.infos) == 1
    assert "no tracks" in result.infos[0].message.lower()


def test_validator_detects_empty_segments(valid_track, valid_plan):
    object.__setattr__(valid_track, 'segments', [])
    
    validator = RenderPlanValidator()
    result = validator.validate(valid_plan)
    
    # Info severity for empty segments
    assert result.is_valid is True
    assert len(result.infos) == 1
    assert "no segments" in result.infos[0].message.lower()


def test_validator_detects_out_of_bounds_segment(valid_segment, valid_plan):
    object.__setattr__(valid_segment.timeline_end, 'time_seconds', 20.0) # metadata duration is 10.0
    
    validator = RenderPlanValidator()
    result = validator.validate(valid_plan)
    
    assert result.is_valid is False
    assert any("extends beyond" in e.message.lower() for e in result.errors)


def test_validator_detects_invalid_instruction_structure(valid_segment, valid_plan):
    instruction = valid_segment.instructions[0]
    
    # Missing instruction_type
    object.__setattr__(instruction, 'instruction_type', "")
    
    validator = RenderPlanValidator()
    result = validator.validate(valid_plan)
    
    assert result.is_valid is False
    assert any("missing an instruction_type" in e.message.lower() for e in result.errors)
    
    # Fix type, break parameters
    object.__setattr__(instruction, 'instruction_type', "crop")
    object.__setattr__(instruction, 'parameters', None)
    
    result2 = validator.validate(valid_plan)
    assert result2.is_valid is False
    assert any("dictionary" in e.message.lower() for e in result2.errors)


def test_validator_detects_out_of_order_segments(valid_track, valid_segment, valid_plan):
    segment2 = RenderSegment(
        id=uuid.uuid4(),
        source_reference="video2.mp4",
        timeline_start=TimelinePosition(time_seconds=2.0), # Starts before valid_segment ends, but more importantly, let's put it first in the list while it has a later start time
        timeline_end=TimelinePosition(time_seconds=6.0),
        source_start=TimelinePosition(time_seconds=0.0),
        source_end=TimelinePosition(time_seconds=4.0),
    )
    
    # Put segments out of order based on start time
    object.__setattr__(valid_track, 'segments', [segment2, valid_segment]) # segment2 starts at 2.0, valid_segment starts at 0.0
    
    validator = RenderPlanValidator()
    result = validator.validate(valid_plan)
    
    assert result.is_valid is False
    assert any("out of order" in e.message.lower() for e in result.errors)
