from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.editing.domain.models.items import Clip
from src.editing.domain.models.project import EditingProject
from src.editing.domain.models.timeline import Timeline


@dataclass(frozen=True)
class ClipSequence:
    """
    Represents the ordered sequence of editorial clip decisions.
    Utilizes the canonical Clip domain model as the single source of truth.
    This is NOT the Timeline. The Timeline represents project structure,
    while ClipSequence represents editorial sequencing decisions.
    """
    clips: List[Clip]


@dataclass(frozen=True)
class ClipBuildingRequest:
    """
    Represents everything required to assemble clips.
    """
    project: EditingProject
    timeline: Timeline
    building_configuration: Optional[Dict[str, Any]] = field(default_factory=dict)
