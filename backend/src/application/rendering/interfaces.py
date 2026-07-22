from typing import Protocol, Any, Dict, Optional

from src.application.execution_models import (
    ValidatedRenderPlan,
    RenderExecutionResult,
)
from src.application.rendering.models import RenderProgress
from src.application.rendering.telemetry import RenderExecutionEvent

class IRenderExecutionService(Protocol):
    """
    Application-level abstraction for executing a render plan.
    Preserves dependency inversion by separating orchestration from concrete execution.
    """
    async def execute_plan(
        self,
        validated_plan: ValidatedRenderPlan,
        output_destination: str,
        execution_options: Optional[Dict[str, Any]] = None
    ) -> RenderExecutionResult:
        ...


class IRenderProgressObserver(Protocol):
    """
    Contract for receiving progress updates.
    Observers consume progress snapshots but never own or mutate the progress state.
    """
    def on_progress(self, progress: RenderProgress) -> None:
        ...


class IRenderTelemetryObserver(Protocol):
    """
    Contract for receiving execution telemetry events.
    Observers are strictly passive: they may consume events but must never mutate 
    telemetry state or influence orchestration decisions.
    """
    def on_event(self, event: RenderExecutionEvent) -> None:
        ...
