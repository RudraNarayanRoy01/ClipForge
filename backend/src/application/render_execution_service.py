import time
import logging
from typing import Dict, Any, Optional

from src.application.execution_models import (
    ValidatedRenderPlan,
    RenderExecutionRequest,
    RenderExecutionResult,
    RenderFailureCategory,
)
from src.domain.contracts.render_backend import IRenderBackend

logger = logging.getLogger(__name__)

class RenderExecutionService:
    """
    Application service responsible for orchestrating the execution of a ValidatedRenderPlan.
    It delegates actual rendering to an injected IRenderBackend, handling failures gracefully 
    by translating them into structured execution results.
    """
    
    def __init__(self, backend: IRenderBackend):
        self._backend = backend

    async def execute_plan(
        self, 
        validated_plan: ValidatedRenderPlan, 
        output_destination: str,
        execution_options: Optional[Dict[str, Any]] = None
    ) -> RenderExecutionResult:
        """
        Orchestrates the rendering process by creating a request and passing it to the backend.
        
        Args:
            validated_plan: A RenderPlan wrapped in ValidatedRenderPlan, ensuring it has passed validation.
            output_destination: Where the rendered output should be saved.
            execution_options: Optional configuration for execution.
            
        Returns:
            RenderExecutionResult: Structured result of the execution.
        """
        request = RenderExecutionRequest(
            validated_plan=validated_plan,
            output_destination=output_destination,
            execution_options=execution_options or {}
        )
        
        start_time = time.monotonic()
        
        try:
            logger.info(f"Starting execution of RenderPlan {validated_plan.plan.id}")
            result = await self._backend.execute(request)
            return result
        except Exception as e:
            # Catching generic Exception because backends might raise anything (e.g. ffmpeg errors, etc.)
            # The service translates these to a structured, backend-agnostic failure result.
            duration = time.monotonic() - start_time
            logger.exception(f"Backend execution failed for RenderPlan {validated_plan.plan.id}")
            return RenderExecutionResult.failure(
                duration_seconds=duration,
                category=RenderFailureCategory.INTERNAL_ERROR,
                message="An unexpected error occurred during backend execution.",
                details={"error_type": type(e).__name__, "error_message": str(e)}
            )
