import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

# --- VALUE OBJECTS ---
@dataclass(frozen=True)
class TimeRange:
    start_time: float
    end_time: float
    
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    def __post_init__(self):
        if self.start_time < 0 or self.end_time < self.start_time:
            raise ValueError("Invalid TimeRange: end_time must be >= start_time >= 0")

@dataclass(frozen=True)
class Resolution:
    width: int
    height: int

@dataclass(frozen=True)
class AiConfidenceScore:
    score: float
    
    def __post_init__(self):
        if not (0.0 <= self.score <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")

@dataclass(frozen=True)
class WordLevelTimestamp:
    word: str
    time_range: TimeRange
    confidence: AiConfidenceScore = field(default_factory=lambda: AiConfidenceScore(1.0))

@dataclass(frozen=True)
class SpeakerSegment:
    speaker_id: str
    time_range: TimeRange

@dataclass(frozen=True)
class EnergySegment:
    time_range: TimeRange
    intensity_score: float # 0.0 to 1.0

@dataclass(frozen=True)
class SilenceSegment:
    time_range: TimeRange

@dataclass(frozen=True)
class SceneBoundary:
    scene_id: str
    time_range: TimeRange

@dataclass(frozen=True)
class FaceBoundingBox:
    timestamp: float
    x: float
    y: float
    w: float
    h: float
    speaker_id: Optional[str] = None

@dataclass(frozen=True)
class EmotionSegment:
    time_range: TimeRange
    dominant_emotion: str # happy, sad, angry, surprised, neutral
    confidence: AiConfidenceScore

@dataclass(frozen=True)
class GestureEvent:
    timestamp: float
    gesture_type: str # pointing, clapping, arms_raised
    confidence: AiConfidenceScore

@dataclass(frozen=True)
class ObjectDetection:
    timestamp: float
    label: str
    confidence: AiConfidenceScore

@dataclass(frozen=True)
class OCREvent:
    timestamp: float
    text: str

@dataclass(frozen=True)
class TopicSegment:
    time_range: TimeRange
    title: str
    summary: str

@dataclass(frozen=True)
class GeneratedCaption:
    time_range: TimeRange
    text: str
    style_metadata: Dict[str, Any] = field(default_factory=dict)

# --- ENTITIES & AGGREGATE ROOTS ---
@dataclass
class Project:
    """Aggregate Root"""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = "Untitled Project"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "created"

@dataclass
class VideoAsset:
    """Entity belonging to Project"""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    project_id: uuid.UUID = field(default_factory=uuid.uuid4) # Should link to Project
    file_path: str = ""
    duration: float = 0.0
    resolution: Resolution = field(default_factory=lambda: Resolution(1920, 1080))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ClipSegment:
    """Entity belonging to Project, extracted from VideoAsset"""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    project_id: uuid.UUID = field(default_factory=uuid.uuid4)
    video_asset_id: uuid.UUID = field(default_factory=uuid.uuid4)
    boundaries: TimeRange = field(default_factory=lambda: TimeRange(0, 0))
    title: str = ""
    hook_text: str = ""
    hashtags: List[str] = field(default_factory=list)
    captions: List[GeneratedCaption] = field(default_factory=list)
    thumbnail_timestamp: float = 0.0
    virality_score: int = 0
    ai_rationale: str = ""
    user_approved: bool = False
    
    @property
    def duration(self) -> float:
        return self.boundaries.duration()

@dataclass
class TimelineContext:
    """Aggregate Root: The central unified matrix that holds all extracted metadata"""
    video_asset_id: uuid.UUID
    words: List[WordLevelTimestamp] = field(default_factory=list)
    speakers: List[SpeakerSegment] = field(default_factory=list)
    energy: List[EnergySegment] = field(default_factory=list)
    silences: List[SilenceSegment] = field(default_factory=list)
    scenes: List[SceneBoundary] = field(default_factory=list)
    faces: List[FaceBoundingBox] = field(default_factory=list)
    emotions: List[EmotionSegment] = field(default_factory=list)
    gestures: List[GestureEvent] = field(default_factory=list)
    objects: List[ObjectDetection] = field(default_factory=list)
    ocr_texts: List[OCREvent] = field(default_factory=list)
    topics: List[TopicSegment] = field(default_factory=list)
