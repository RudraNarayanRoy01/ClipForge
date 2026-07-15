from typing import List, Optional
from pydantic import BaseModel, Field


class Topic(BaseModel):
    """
    Represents a distinct subject or theme discussed in the video.
    Immutable to ensure data integrity across the pipeline.
    """
    name: str = Field(description="A concise concept representing the primary topic discussed. Avoid full sentences.")
    description: str = Field(description="A brief description of the topic.")
    confidence: float = Field(description="Confidence score of this topic extraction between 0.0 and 1.0.")
    start_time: float = Field(description="Start time of the topic in seconds.")
    end_time: float = Field(description="End time of the topic in seconds.")
    reasoning: Optional[str] = Field(default=None, description="Reasoning for extracting this topic.")

    class Config:
        frozen = True


class Entity(BaseModel):
    """
    Represents a specific person, organization, location, or concept in the video.
    """
    name: str = Field(description="The exact name of the extracted entity.")
    entity_type: str = Field(description="Type of the entity (e.g., People, Companies, Brands, Products, Technologies, Organizations, Locations, Events).")
    confidence: float = Field(description="Confidence score of this entity extraction between 0.0 and 1.0.")
    reasoning: Optional[str] = Field(default=None, description="Evidence from the transcript supporting this entity.")

    class Config:
        frozen = True


class Hook(BaseModel):
    """
    Represents an engaging segment at the beginning or within the video designed to capture attention.
    """
    text: str
    start_time: float
    end_time: float
    score: float
    reasoning: Optional[str] = None

    class Config:
        frozen = True


class Highlight(BaseModel):
    """
    Represents a highly engaging, important, or entertaining segment of the video.
    """
    title: str
    description: str
    start_time: float
    end_time: float
    viral_score: float
    reasoning: Optional[str] = None

    class Config:
        frozen = True


class Sentiment(BaseModel):
    """
    Represents the overall emotional tone or sentiment of a segment or the entire video.
    """
    primary_emotion: str
    score: float
    reasoning: Optional[str] = None

    class Config:
        frozen = True


class VideoUnderstandingResult(BaseModel):
    """
    The complete result of a video understanding analysis request.
    Provider-agnostic domain model.
    """
    topics: List[Topic] = Field(default_factory=list)
    entities: List[Entity] = Field(default_factory=list)
    hooks: List[Hook] = Field(default_factory=list)
    highlights: List[Highlight] = Field(default_factory=list)
    overall_sentiment: Optional[Sentiment] = None
    summary: Optional[str] = None

    class Config:
        frozen = True


class VideoAnalysisRequest(BaseModel):
    """
    Request payload for starting a video understanding job.
    """
    video_id: str
    transcript_text: str
    target_audiences: List[str] = Field(default_factory=list)
    custom_instructions: Optional[str] = Field(
        default=None, 
        description="Optional instructions to guide the AI's analysis"
    )

    class Config:
        frozen = True
