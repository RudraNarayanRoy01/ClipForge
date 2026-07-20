from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.editing.domain.models.export import ExportProfile
from src.editing.domain.models.timeline import Timeline


@dataclass(frozen=True)
class EditingProjectMetadata:
    """
    Metadata for the EditingProject.
    """
    created_at: datetime
    updated_at: datetime
    version: int
    author_id: Optional[str] = None


@dataclass(frozen=True)
class EditingProject:
    """
    Aggregate root for the editing domain.
    Owns Timeline, ExportProfile, and Metadata.
    """
    id: UUID
    title: str
    metadata: EditingProjectMetadata
    timeline: Timeline
    export_profile: ExportProfile
