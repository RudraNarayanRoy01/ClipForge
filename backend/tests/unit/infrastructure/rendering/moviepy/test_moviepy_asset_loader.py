import uuid
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

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
from src.infrastructure.rendering.moviepy.structures import MoviePyResourcePool
from src.infrastructure.rendering.moviepy.validation import MoviePyAssetValidator
from src.infrastructure.rendering.moviepy.loader import MoviePyAssetLoader

@pytest.fixture
def dummy_render_plan():
    segment1 = RenderSegment(
        id=uuid.uuid4(),
        source_reference="/fake/path/video1.mp4",
        timeline_start=TimelinePosition(0.0),
        timeline_end=TimelinePosition(5.0),
        source_start=TimelinePosition(0.0),
        source_end=TimelinePosition(5.0)
    )
    segment2 = RenderSegment(
        id=uuid.uuid4(),
        source_reference="/fake/path/audio1.mp3",
        timeline_start=TimelinePosition(0.0),
        timeline_end=TimelinePosition(5.0),
        source_start=TimelinePosition(0.0),
        source_end=TimelinePosition(5.0)
    )
    
    layer_video = RenderLayer(
        id=uuid.uuid4(),
        category=LayerCategory.VIDEO,
        name="Main Video",
        z_index=0,
        tracks=[RenderTrack(id=uuid.uuid4(), name="Track 1", segments=[segment1])]
    )
    layer_audio = RenderLayer(
        id=uuid.uuid4(),
        category=LayerCategory.AUDIO,
        name="Main Audio",
        z_index=1,
        tracks=[RenderTrack(id=uuid.uuid4(), name="Track 2", segments=[segment2])]
    )
    
    metadata = RenderMetadata(
        resolution=RenderResolution(1920, 1080),
        frame_rate=FrameRate(30.0),
        duration_seconds=5.0,
        aspect_ratio=AspectRatio(16, 9)
    )
    
    return RenderPlan(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        metadata=metadata,
        layers=[layer_video, layer_audio]
    )

def test_validator_success(tmp_path):
    # Create dummy files
    video_path = tmp_path / "test.mp4"
    video_path.touch()
    
    # Should not raise
    MoviePyAssetValidator.validate_reference(str(video_path), "video")

def test_validator_file_not_found():
    with pytest.raises(FileNotFoundError):
        MoviePyAssetValidator.validate_reference("/nonexistent/video.mp4", "video")

def test_validator_unsupported_type(tmp_path):
    txt_path = tmp_path / "test.txt"
    txt_path.touch()
    
    with pytest.raises(ValueError, match="Unsupported video format"):
        MoviePyAssetValidator.validate_reference(str(txt_path), "video")

@patch("src.infrastructure.rendering.moviepy.loader.VideoFileClip")
@patch("src.infrastructure.rendering.moviepy.loader.AudioFileClip")
@patch("src.infrastructure.rendering.moviepy.loader.MoviePyAssetValidator.validate_reference")
def test_loader_populates_pool(mock_validate, mock_audio_clip, mock_video_clip, dummy_render_plan):
    mock_video_clip.return_value = MagicMock()
    mock_audio_clip.return_value = MagicMock()
    
    pool = MoviePyResourcePool()
    
    MoviePyAssetLoader.load_assets(dummy_render_plan, pool)
    
    assert mock_validate.call_count == 2
    assert len(pool.video_clips) == 1
    assert len(pool.audio_clips) == 1

def test_resource_pool_cleanup():
    pool = MoviePyResourcePool()
    mock_clip1 = MagicMock()
    mock_clip2 = MagicMock()
    
    pool.add_video_clip(uuid.uuid4(), mock_clip1)
    pool.add_audio_clip(uuid.uuid4(), mock_clip2)
    
    pool.cleanup()
    
    mock_clip1.close.assert_called_once()
    mock_clip2.close.assert_called_once()
    assert len(pool.video_clips) == 0
    assert len(pool.audio_clips) == 0
