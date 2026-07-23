from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from src.editing.domain.models.export import ExportProfile
from src.editing.domain.models.project import EditingProject
from src.editing.domain.models.state import TimelineState
from src.editing.domain.pipeline.editing import EditingSequence
from src.editing.domain.pipeline.subtitles import SubtitleTrack


@dataclass(frozen=True)
class FinalizedEdit:
    """
    Represents the final editing output produced by Milestone 5.
    Represents editorial execution intent, not renderer instructions.
    Completely independent of rendering engines (FFmpeg, MoviePy, etc.).
    Describes only WHAT should be rendered.
    """
    timeline: TimelineState
    editing_sequence: EditingSequence
    subtitle_track: SubtitleTrack
    export_profile: ExportProfile
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class ExportPlanningRequest:
    """
    Represents everything required to prepare an EditingProject for export.
    Canonical input for export planning.
    """
    project: EditingProject
    timeline: TimelineState
    editing_sequence: EditingSequence
    subtitle_track: SubtitleTrack
    export_profile: ExportProfile
