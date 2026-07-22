import os
from pathlib import Path
from typing import Set

from src.infrastructure.rendering.moviepy.timeline import MoviePyTimeline

class MoviePyAssetValidator:
    """
    Validates infrastructure assets prior to loading.
    
    Ensures assets exist, are readable, and are of a supported media type,
    providing fast-fail semantics without actually instantiating backend resources.
    """
    
    # Generic categories mapping to supported file extensions
    SUPPORTED_VIDEO_EXT: Set[str] = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    SUPPORTED_AUDIO_EXT: Set[str] = {".mp3", ".wav", ".aac", ".m4a", ".flac"}
    SUPPORTED_IMAGE_EXT: Set[str] = {".png", ".jpg", ".jpeg", ".webp"}
    SUPPORTED_SUBTITLE_EXT: Set[str] = {".srt", ".vtt"}

    @classmethod
    def validate_reference(cls, source_reference: str, expected_category: str) -> None:
        """
        Validates a single asset reference.
        
        Args:
            source_reference: The path to the media file.
            expected_category: "video", "audio", "image", or "subtitle".
            
        Raises:
            FileNotFoundError: If the asset does not exist.
            PermissionError: If the asset exists but is not readable.
            ValueError: If the asset type is unsupported or invalid.
        """
        if not source_reference:
            raise ValueError("Asset reference cannot be empty.")
            
        path = Path(source_reference)
        
        if not path.exists():
            raise FileNotFoundError(f"Asset not found at path: {source_reference}")
            
        if not path.is_file():
            raise ValueError(f"Asset path is not a file: {source_reference}")
            
        if not os.access(path, os.R_OK):
            raise PermissionError(f"Asset is not readable: {source_reference}")
            
        ext = path.suffix.lower()
        
        if expected_category == "video" and ext not in cls.SUPPORTED_VIDEO_EXT:
            raise ValueError(f"Unsupported video format '{ext}' for asset: {source_reference}")
        elif expected_category == "audio" and ext not in cls.SUPPORTED_AUDIO_EXT:
            raise ValueError(f"Unsupported audio format '{ext}' for asset: {source_reference}")
        elif expected_category == "image" and ext not in cls.SUPPORTED_IMAGE_EXT:
            raise ValueError(f"Unsupported image format '{ext}' for asset: {source_reference}")
        elif expected_category == "subtitle" and ext not in cls.SUPPORTED_SUBTITLE_EXT:
            raise ValueError(f"Unsupported subtitle format '{ext}' for asset: {source_reference}")
        elif expected_category not in {"video", "audio", "image", "subtitle"}:
            raise ValueError(f"Unknown asset category '{expected_category}' for asset: {source_reference}")


class MoviePyOutputValidator:
    """
    Validates render specification semantics and timeline consistency prior to output composition.
    Does not validate execution environment or filesystem concerns.
    """
    
    @classmethod
    def validate_timeline(cls, timeline: MoviePyTimeline) -> None:
        """
        Validates the semantic consistency of a composed timeline graph.
        
        Args:
            timeline: The immutable timeline to validate.
            
        Raises:
            ValueError: If the timeline is semantically invalid for rendering.
        """
        if not timeline:
            raise ValueError("Timeline cannot be None")
            
        if timeline.context is None:
            raise ValueError("Timeline context cannot be missing, graph integrity compromised")
            
        if not timeline.has_video and not timeline.has_audio:
            raise ValueError("Timeline is empty: must contain at least one visual or audio track")
            
        if timeline.context.duration_seconds <= 0:
            raise ValueError(f"Timeline duration must be positive, got {timeline.context.duration_seconds}")
            
        if timeline.context.resolution_width <= 0 or timeline.context.resolution_height <= 0:
            raise ValueError(
                f"Timeline resolution must be positive, got "
                f"{timeline.context.resolution_width}x{timeline.context.resolution_height}"
            )

