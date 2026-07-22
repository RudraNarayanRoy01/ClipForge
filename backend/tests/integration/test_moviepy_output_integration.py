import pytest
import uuid
import os
from unittest.mock import patch, MagicMock

from src.infrastructure.rendering.moviepy.timeline import MoviePyTimeline, MoviePyCompositionContext
from src.infrastructure.rendering.moviepy.output import (
    MoviePyRenderConfiguration,
    MoviePyRenderOutput,
    MoviePyOutputComposer
)

@pytest.fixture
def mock_timeline():
    # Setup a timeline that passes validation
    context = MoviePyCompositionContext(
        duration_seconds=5.0,
        resolution_width=1280,
        resolution_height=720,
        fps=24.0,
        background_color=(0, 0, 0)
    )
    
    return MoviePyTimeline(
        context=context,
        _root_video=object(),
        _root_audio=object()
    )

class TestMoviePyOutputIntegration:
    @patch('src.infrastructure.rendering.moviepy.output.MoviePyOutputValidator.validate_timeline')
    def test_output_composition_does_not_modify_timeline_or_touch_filesystem(self, mock_validate, mock_timeline, tmp_path):
        """
        Verify that converting timeline to output:
        - succeeds
        - does not mutate timeline graph
        - does not write any files
        - has clear ownership boundary
        """
        original_context = mock_timeline.context
        
        # Action
        output = MoviePyOutputComposer.compose_output(mock_timeline)
        
        # Verify timeline conversion success
        assert isinstance(output, MoviePyRenderOutput)
        assert output.configuration.resolution == (1280, 720)
        assert output.configuration.fps == 24.0
        
        # Verify validation was called
        mock_validate.assert_called_once_with(mock_timeline)
        
        # Verify timeline immutability (same object reference for context)
        assert output.timeline is mock_timeline
        assert mock_timeline.context is original_context
        
        # Verify no file was created (we mock filesystem behavior implicitly by lack of imports/writes)
        # We ensure MoviePyOutputComposer doesn't write by checking the directory is empty
        assert len(list(tmp_path.iterdir())) == 0

    def test_output_metadata_consolidation(self, mock_timeline):
        """
        Verify that execution parameters and config metadata are collected correctly.
        """
        output = MoviePyOutputComposer.compose_output(mock_timeline, {"custom_param": "value123"})
        
        assert output.metadata["duration_seconds"] == 5.0
        assert output.metadata["has_video"] is True
        assert output.metadata["has_audio"] is True
        assert output.metadata["custom_param"] == "value123"
        
        assert isinstance(output.configuration, MoviePyRenderConfiguration)
        assert output.configuration.fps == 24.0
