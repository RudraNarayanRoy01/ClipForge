from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class MediaMetadata(BaseModel):
    """DTO representing retrieved media metadata."""
    duration_seconds: float
    width: int
    height: int
    fps: float
    has_audio: bool
    format_name: str
    bitrate: Optional[int] = None
    extra_info: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        frozen = True

class ClipExtractionRequest(BaseModel):
    """DTO for requesting clip extraction from media."""
    source_path: str
    output_path: str
    start_time: float
    end_time: float
    target_width: Optional[int] = None
    target_height: Optional[int] = None
    maintain_aspect_ratio: bool = True
    watermark_path: Optional[str] = None
    
    class Config:
        frozen = True

class AudioExtractionRequest(BaseModel):
    """DTO for requesting audio track extraction."""
    source_path: str
    output_path: str
    target_sample_rate: int = 16000
    target_channels: int = 1
    
    class Config:
        frozen = True

class ThumbnailGenerationRequest(BaseModel):
    """DTO for generating a thumbnail from media."""
    source_path: str
    output_path: str
    timestamp: float
    target_width: Optional[int] = None
    target_height: Optional[int] = None
    
    class Config:
        frozen = True

class GenericMediaProcessingRequest(BaseModel):
    """DTO for arbitrary media operations that don't fit standard categories."""
    source_path: str
    output_path: str
    operation_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        frozen = True

class MediaProcessingResponse(BaseModel):
    """DTO representing the result of a media processing operation."""
    success: bool
    output_path: str
    execution_time_seconds: float
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    class Config:
        frozen = True
