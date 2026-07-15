from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from src.media.dtos import MediaMetadata
from src.transcription.dtos import Transcript
from src.video_understanding.dtos import VideoUnderstandingResult


class KnowledgeStatus(str, Enum):
    """
    Indicates whether downstream systems can safely consume the knowledge.
    """
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    COMPLETE = "COMPLETE"
    INVALID = "INVALID"


class KnowledgeMetadata(BaseModel):
    """
    Provider-independent metadata describing the knowledge snapshot itself.
    """
    schema_version: str = Field(description="Version of the knowledge schema")
    knowledge_version: str = Field(description="Version of the knowledge extraction logic")
    processing_timestamp: datetime = Field(description="When this knowledge snapshot was generated")
    provider_identifier: str = Field(description="Generic identifier for the underlying providers used")
    source_version: str = Field(description="Version or hash of the source media used")

    class Config:
        frozen = True


class VideoKnowledge(BaseModel):
    """
    The canonical domain model representing everything ClipForge knows about a processed video.
    This is an immutable snapshot serving as a single source of truth for downstream systems.
    It aggregates validated domain concepts rather than duplicating them.
    """
    status: KnowledgeStatus = Field(description="Overall completeness status of the knowledge")
    metadata: KnowledgeMetadata = Field(description="Information about the knowledge snapshot")
    
    media_metadata: Optional[MediaMetadata] = Field(
        default=None, 
        description="Extracted technical metadata of the video"
    )
    transcript: Optional[Transcript] = Field(
        default=None, 
        description="The complete transcription of the video"
    )
    understanding: Optional[VideoUnderstandingResult] = Field(
        default=None, 
        description="The semantic understanding of the video content (topics, entities, hooks, etc.)"
    )

    class Config:
        frozen = True
