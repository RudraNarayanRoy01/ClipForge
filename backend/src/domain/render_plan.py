import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from enum import Enum, auto

class LayerCategory(Enum):
    VIDEO = auto()
    AUDIO = auto()
    SUBTITLE = auto()
    OVERLAY = auto()

# --- VALUE OBJECTS ---

@dataclass(frozen=True)
class RenderResolution:
    width: int
    height: int

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Resolution width and height must be positive.")

@dataclass(frozen=True)
class FrameRate:
    fps: float

    def __post_init__(self):
        if self.fps <= 0:
            raise ValueError("Frame rate must be greater than 0.")

@dataclass(frozen=True)
class AspectRatio:
    width_ratio: int
    height_ratio: int

    def __post_init__(self):
        if self.width_ratio <= 0 or self.height_ratio <= 0:
            raise ValueError("Aspect ratio components must be positive.")

@dataclass(frozen=True)
class TimelinePosition:
    time_seconds: float

    def __post_init__(self):
        if self.time_seconds < 0:
            raise ValueError("Timeline position cannot be negative.")

@dataclass(frozen=True)
class SafeZone:
    top_margin_percent: float
    bottom_margin_percent: float
    left_margin_percent: float
    right_margin_percent: float

    def __post_init__(self):
        for margin in (self.top_margin_percent, self.bottom_margin_percent, self.left_margin_percent, self.right_margin_percent):
            if not (0.0 <= margin <= 100.0):
                raise ValueError("Margins must be between 0 and 100 percent.")

@dataclass(frozen=True)
class RenderBounds:
    x: float
    y: float
    width: float
    height: float

@dataclass(frozen=True)
class RenderTransform:
    scale_x: float = 1.0
    scale_y: float = 1.0
    bounds: Optional[RenderBounds] = None
    opacity: float = 1.0

# --- ENTITIES ---

@dataclass(frozen=True)
class RenderInstruction:
    """
    Generic render instruction describing intent (e.g., 'crop', 'fade', 'duck_audio').
    Contains no implementation logic.
    """
    instruction_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class RenderSegment:
    """Deterministic timeline fragment."""
    id: uuid.UUID
    source_reference: str
    timeline_start: TimelinePosition
    timeline_end: TimelinePosition
    source_start: TimelinePosition
    source_end: TimelinePosition
    instructions: List[RenderInstruction] = field(default_factory=list)
    visible: bool = True

    def __post_init__(self):
        if self.timeline_end.time_seconds < self.timeline_start.time_seconds:
            raise ValueError("timeline_end cannot be before timeline_start")
        if self.source_end.time_seconds < self.source_start.time_seconds:
            raise ValueError("source_end cannot be before source_start")

@dataclass(frozen=True)
class RenderTrack:
    """Describes ordered media within a layer."""
    id: uuid.UUID
    name: str
    segments: List[RenderSegment] = field(default_factory=list)
    
    def __post_init__(self):
        # Validate that segments are ordered by timeline_start
        for i in range(1, len(self.segments)):
            if self.segments[i].timeline_start.time_seconds < self.segments[i-1].timeline_start.time_seconds:
                raise ValueError("Segments within a RenderTrack must be deterministically ordered by start time.")

@dataclass(frozen=True)
class RenderLayer:
    """Logical grouping of tracks, describing intent only."""
    id: uuid.UUID
    category: LayerCategory
    name: str
    z_index: int
    tracks: List[RenderTrack] = field(default_factory=list)

@dataclass(frozen=True)
class RenderMetadata:
    """Renderer-independent metadata."""
    resolution: RenderResolution
    frame_rate: FrameRate
    duration_seconds: float
    aspect_ratio: AspectRatio
    orientation: str = "landscape" # e.g., "landscape", "portrait", "square"
    safe_zones: List[SafeZone] = field(default_factory=list)
    
    def __post_init__(self):
        if self.duration_seconds < 0:
            raise ValueError("Duration cannot be negative.")

# --- AGGREGATE ROOT ---

@dataclass(frozen=True)
class RenderPlan:
    """
    The RenderPlan Aggregate Root.
    Immutable, deterministic, and serializable specification for rendering.
    """
    id: uuid.UUID
    project_id: uuid.UUID
    metadata: RenderMetadata
    layers: List[RenderLayer] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.layers:
            raise ValueError("RenderPlan must contain at least one RenderLayer.")
        
        # Verify deterministic layer ordering by z_index
        z_indices = [layer.z_index for layer in self.layers]
        if z_indices != sorted(z_indices):
            raise ValueError("Layers must be deterministically ordered by z_index.")
