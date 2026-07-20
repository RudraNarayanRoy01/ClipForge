from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import UUID

from src.editing.domain.models.items import Subtitle
from src.editing.domain.models.timeline import Timeline
from src.editing.domain.pipeline.editing import EditingSequence


@dataclass(frozen=True)
class SubtitleTrack:
    """
    Represents the completed subtitle layer.
    Contains only subtitle information.
    Contains no renderer-specific information.
    Contains no font engine implementation.
    Contains no subtitle rendering logic.
    """
    id: UUID
    subtitles: List[Subtitle]


@dataclass(frozen=True)
class SubtitleGenerationRequest:
    """
    Represents everything required to generate subtitle tracks.
    Future AI implementations will consume this contract.
    """
    editing_sequence: EditingSequence
    timeline: Timeline
    subtitle_preferences: Optional[Dict[str, Any]] = field(default_factory=dict)
