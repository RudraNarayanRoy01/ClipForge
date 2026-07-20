from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from src.editing.domain.models.project import EditingProject
from src.editing.domain.models.timeline import Timeline


@dataclass(frozen=True)
class TimelinePlanningRequest:
    """
    Represents everything required to construct a timeline.
    This object represents the complete input to Timeline Planning.
    """
    project: EditingProject
    planning_configuration: Optional[Dict[str, Any]] = field(default_factory=dict)
    planning_constraints: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class TimelinePlanningResult:
    """
    Represents the completed result of Timeline Planning.
    This becomes the canonical input to Clip Building.
    """
    timeline: Timeline
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    diagnostics: Optional[Dict[str, Any]] = field(default_factory=dict)
