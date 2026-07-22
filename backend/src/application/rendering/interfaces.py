from typing import Protocol, Any, Dict, Optional

from src.application.execution_models import (
    ValidatedRenderPlan,
    RenderExecutionResult,
)

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
