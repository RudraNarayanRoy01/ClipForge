from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class SemanticEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    stream_id: str
    start_time_ms: int
    end_time_ms: int
    confidence: float = Field(ge=0.0, le=1.0)
    modality: Literal["AUDIO", "VISUAL", "TEXT", "SYSTEM", "SENSOR"]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TranscriptEvent(SemanticEvent):
    modality: Literal["AUDIO", "VISUAL", "TEXT", "SYSTEM", "SENSOR"] = "TEXT"
    text: str
    speaker_id: Optional[str] = None

class EmotionEvent(SemanticEvent):
    modality: Literal["AUDIO", "VISUAL", "TEXT", "SYSTEM", "SENSOR"]
    emotion: str
    intensity: float = Field(ge=0.0, le=1.0)

class SceneEvent(SemanticEvent):
    modality: Literal["AUDIO", "VISUAL", "TEXT", "SYSTEM", "SENSOR"] = "VISUAL"
    description: str
    tags: List[str] = Field(default_factory=list)

class OCREvent(SemanticEvent):
    modality: Literal["AUDIO", "VISUAL", "TEXT", "SYSTEM", "SENSOR"] = "VISUAL"
    text: str
    bounding_box: tuple
