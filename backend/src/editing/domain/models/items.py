from abc import ABC
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.editing.domain.enums.items import ScalingMode, TimelineItemType
from src.editing.domain.enums.transitions import TransitionType
from src.editing.domain.value_objects.spatial import BoundingBox, Position
from src.editing.domain.value_objects.time import Time, TimeRange


@dataclass(frozen=True, kw_only=True)
class TimelineItem(ABC):
    """
    Base abstraction for any item placed on a timeline.
    Extensible for future items like Marker, AudioRegion, etc.
    """
    id: UUID
    item_type: TimelineItemType
    timeline_time_range: TimeRange
    source_time_range: Optional[TimeRange] = None


@dataclass(frozen=True, kw_only=True)
class Clip(TimelineItem):
    """
    Represents video or audio media on the timeline.
    """
    asset_id: UUID
    playback_speed: float = 1.0
    scaling_mode: ScalingMode = ScalingMode.FIT


@dataclass(frozen=True, kw_only=True)
class Subtitle(TimelineItem):
    """
    Represents text overlay with timing.
    """
    text: str
    style_reference_id: Optional[str] = None
    position: Optional[Position] = None


@dataclass(frozen=True, kw_only=True)
class Overlay(TimelineItem):
    """
    Represents an image, graphic, or secondary video overlay.
    """
    asset_id: UUID
    bounding_box: BoundingBox
    opacity: float = 1.0


@dataclass(frozen=True)
class Transition(TimelineItem):
    """
    Represents a transition effect between items.
    """
    transition_type: TransitionType
    duration: Time
