import os
from pathlib import Path
from typing import Set

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
