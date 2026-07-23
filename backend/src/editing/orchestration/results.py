from dataclasses import dataclass

from src.editing.domain.pipeline.export import RenderPlan
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
    render_plan: RenderPlan
    metadata: ExecutionMetadata = ExecutionMetadata()
    diagnostics: ExecutionDiagnostics = ExecutionDiagnostics()
