from dataclasses import dataclass

from src.editing.domain.pipeline.export import FinalizedEdit
from src.editing.orchestration.value_objects import (
    ExecutionDiagnostics,
    ExecutionMetadata,
)


@dataclass(frozen=True)
class EditingOrchestrationResult:
    """
    Immutable orchestration result representing the completed execution 
    of the editing workflow.
    """
    finalized_edit: FinalizedEdit
    metadata: ExecutionMetadata = ExecutionMetadata()
    diagnostics: ExecutionDiagnostics = ExecutionDiagnostics()
