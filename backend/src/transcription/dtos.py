from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class TranscriptionWord(BaseModel):
    """
    Represents a single transcribed word with timing and confidence metadata.
    Immutable to ensure data integrity across the pipeline.
    """
    text: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    confidence: Optional[float] = None
    speaker: Optional[str] = None
    
    class Config:
        frozen = True


class TranscriptionSegment(BaseModel):
    """
    Represents a logical segment of a transcript (e.g., a sentence or utterance).
    """
    text: str
    start_time: float
    end_time: float
    words: List[TranscriptionWord] = Field(default_factory=list)
    language: Optional[str] = None
    speaker: Optional[str] = None
    confidence: Optional[float] = None
    
    class Config:
        frozen = True


class Transcript(BaseModel):
    """
    The complete result of a transcription process.
    Provider-agnostic domain model.
    """
    full_text: str
    segments: List[TranscriptionSegment] = Field(default_factory=list)
    language: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific or extra metadata")
    
    class Config:
        frozen = True


class TranscriptionRequest(BaseModel):
    """
    Request payload for starting a transcription job.
    """
    media_path: str
    language_hint: Optional[str] = None
    prompt: Optional[str] = Field(default=None, description="Optional prompt to guide transcription context")
    detect_speakers: bool = False
    
    class Config:
        frozen = True


class TranscriptSearchResult(BaseModel):
    """
    Represents a search result containing a matched segment and its associated video asset ID.
    """
    video_asset_id: uuid.UUID
    segment: TranscriptionSegment
    
    class Config:
        frozen = True
