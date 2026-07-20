from dataclasses import dataclass
from typing import List
from uuid import UUID

from src.editing.domain.enums.tracks import TrackType
from src.editing.domain.models.items import TimelineItem
from src.editing.domain.value_objects.time import Time


@dataclass(frozen=True)
class Track:
    """
    Ordered container for TimelineItems.
    """
    id: UUID
    name: str
    type: TrackType
    layer_index: int
    items: List[TimelineItem]
    is_muted: bool = False
    is_hidden: bool = False


@dataclass(frozen=True)
class Timeline:
    """
    The core timeline containing all tracks and explicit duration.
    """
    id: UUID
    tracks: List[Track]
    duration: Time
