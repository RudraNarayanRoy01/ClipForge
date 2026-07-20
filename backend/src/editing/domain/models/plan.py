from dataclasses import dataclass
from datetime import datetime
from typing import Tuple
from uuid import UUID

from src.editing.domain.models.decisions import EditDecision
from src.editing.domain.models.project import EditingProject

@dataclass(frozen=True)
class EditingPlan:
    """
    The canonical business artifact representing an intended edit.
    Aggregates editing decisions and exposes editing metadata.
    Remains immutable and implementation-independent.
    """
    id: UUID
    project: EditingProject
    decisions: Tuple[EditDecision, ...]
    created_at: datetime
    version: int
