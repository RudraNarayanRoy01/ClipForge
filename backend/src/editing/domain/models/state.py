from dataclasses import dataclass, field
from typing import Tuple
from uuid import UUID

from src.editing.domain.enums.tracks import TimelineTrackType
from src.editing.domain.models.items import TimelineItem
from src.editing.domain.value_objects.time import Time


@dataclass(frozen=True, kw_only=True)
class TimelineMetadata:
    """
    Immutable properties of the editable timeline.
    Represents timeline configuration rather than rendering output settings.
    """
    fps: float
    resolution: Tuple[int, int]
    sample_rate: int


@dataclass(frozen=True, kw_only=True)
class TimelineTrack:
    """
    Immutable representation of an independent editing track.
    Acts as an ordered container for timeline items of a specific category.
    """
    id: UUID
    track_type: TimelineTrackType
    items: Tuple[TimelineItem, ...] = field(default_factory=tuple)


@dataclass(frozen=True, kw_only=True)
class TimelineState:
    """
    The canonical editable representation of a project.
    Represents the complete state of the timeline after operations are applied.
    Contains immutable collections of tracks for different domains.
    """
    video_tracks: Tuple[TimelineTrack, ...]
    audio_tracks: Tuple[TimelineTrack, ...]
    overlay_tracks: Tuple[TimelineTrack, ...]
    subtitle_tracks: Tuple[TimelineTrack, ...]
    metadata: TimelineMetadata
    total_duration: Time
