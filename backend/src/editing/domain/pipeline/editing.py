from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from src.editing.domain.models.project import EditingProject
from src.editing.domain.pipeline.clips import ClipSequence


@dataclass(frozen=True)
class EditingSequence:
    """
    Represents the canonical pipeline artifact for editorial editing intent.
    Intentionally minimal and backend-independent. 
    Avoids speculative operations prior to concrete requirements.
    """
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class EditingRequest:
    """
    Represents everything required by the Editing Engine.
    The request describes editing intent only.
    """
    project: EditingProject
    clip_sequence: ClipSequence
    editing_preferences: Optional[Dict[str, Any]] = field(default_factory=dict)
