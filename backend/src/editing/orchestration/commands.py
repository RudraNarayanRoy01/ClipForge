from dataclasses import dataclass

from src.editing.domain.models.project import EditingProject
from src.editing.orchestration.value_objects import (
    ExecutionMetadata,
    ExecutionOptions,
    ExecutionPreferences,
)


@dataclass(frozen=True)
class EditingExecutionCommand:
    """
    Immutable orchestration command representing everything required 
    to execute the complete editing workflow.
    """
    project: EditingProject
    preferences: ExecutionPreferences = ExecutionPreferences()
    options: ExecutionOptions = ExecutionOptions()
    metadata: ExecutionMetadata = ExecutionMetadata()
