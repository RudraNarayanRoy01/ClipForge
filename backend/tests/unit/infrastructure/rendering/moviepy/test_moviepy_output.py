import pytest
import uuid
from dataclasses import FrozenInstanceError

from src.infrastructure.rendering.moviepy.timeline import MoviePyTimeline, MoviePyCompositionContext
from src.infrastructure.rendering.moviepy.output import (
    MoviePyRenderConfiguration,
    MoviePyRenderOutput,
    MoviePyOutputComposer
)

@pytest.fixture
def valid_context():
    return MoviePyCompositionContext(
        duration_seconds=10.0,
        resolution_width=1920,
        resolution_height=1080,
        fps=30.0,
        background_color=(0, 0, 0)
    )

@pytest.fixture
def mock_timeline(valid_context):
    return MoviePyTimeline(
        context=valid_context,
        _root_video=object(),
        _root_audio=object()
    )

class TestMoviePyRenderOutputImmutability:
    def test_configuration_is_immutable(self):
        config = MoviePyRenderConfiguration(fps=30.0, resolution=(1920, 1080))
        with pytest.raises(FrozenInstanceError):
            config.fps = 60.0

    def test_output_is_immutable(self, mock_timeline):
        config = MoviePyRenderConfiguration(fps=30.0, resolution=(1920, 1080))
        output = MoviePyRenderOutput(
            id=uuid.uuid4(),
            timeline=mock_timeline,
            configuration=config
        )
        with pytest.raises(FrozenInstanceError):
            output.configuration = config

class TestMoviePyOutputValidator:
    def test_valid_timeline_passes(self, mock_timeline):
        # Should not raise
        output = MoviePyOutputComposer.compose_output(mock_timeline)
        assert output is not None

    def test_none_timeline_fails(self):
        with pytest.raises(ValueError, match="Timeline cannot be None"):
            MoviePyOutputComposer.compose_output(None)

    def test_empty_timeline_fails(self, valid_context):
        empty_timeline = MoviePyTimeline(context=valid_context, _root_video=None, _root_audio=None)
        with pytest.raises(ValueError, match="must contain at least one visual or audio track"):
            MoviePyOutputComposer.compose_output(empty_timeline)

    def test_zero_duration_fails(self):
        bad_context = MoviePyCompositionContext(
            duration_seconds=0.0, resolution_width=1920, resolution_height=1080, fps=30.0
        )
        bad_timeline = MoviePyTimeline(context=bad_context, _root_video=object(), _root_audio=None)
        with pytest.raises(ValueError, match="duration must be positive"):
            MoviePyOutputComposer.compose_output(bad_timeline)

    def test_invalid_resolution_fails(self):
        bad_context = MoviePyCompositionContext(
            duration_seconds=10.0, resolution_width=0, resolution_height=1080, fps=30.0
        )
        bad_timeline = MoviePyTimeline(context=bad_context, _root_video=object(), _root_audio=None)
        with pytest.raises(ValueError, match="resolution must be positive"):
            MoviePyOutputComposer.compose_output(bad_timeline)

class TestMoviePyOutputComposer:
    def test_metadata_generation(self, mock_timeline):
        custom_metadata = {"export_quality": "high"}
        output = MoviePyOutputComposer.compose_output(mock_timeline, custom_metadata)
        
        assert output.metadata["duration_seconds"] == 10.0
        assert output.metadata["has_video"] is True
        assert output.metadata["has_audio"] is True
        assert output.metadata["export_quality"] == "high"

    def test_configuration_mapping(self, mock_timeline):
        output = MoviePyOutputComposer.compose_output(mock_timeline)
        
        assert output.configuration.fps == 30.0
        assert output.configuration.resolution == (1920, 1080)
        assert output.configuration.background_color == (0, 0, 0)
        
    def test_deterministic_output(self, mock_timeline):
        output1 = MoviePyOutputComposer.compose_output(mock_timeline)
        output2 = MoviePyOutputComposer.compose_output(mock_timeline)
        
        # Identity should be unique
        assert output1.id != output2.id
        
        # But configuration should match exactly given same timeline context
        assert output1.configuration == output2.configuration
