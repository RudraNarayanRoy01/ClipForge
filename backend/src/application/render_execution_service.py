import time
import logging
from typing import Dict, Any, Optional

from src.application.execution_models import (
    ValidatedRenderPlan,
    RenderExecutionRequest,
    RenderExecutionResult,
    RenderFailureCategory,
)
from src.domain.ports import IRenderBackend

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
        Orchestrates the rendering process by extracting domain primitives and passing them to the backend.
        
        Args:
            validated_plan: A RenderPlan wrapped in ValidatedRenderPlan, ensuring it has passed validation.
            output_destination: Where the rendered output should be saved.
            execution_options: Optional configuration for execution.
            
        Returns:
            RenderExecutionResult: Structured result of the execution.
        """
        start_time = time.monotonic()
        
        try:
            logger.info(f"Starting execution of RenderPlan {validated_plan.plan.id}")
            
            # Application layer translates and delegates to Domain port
            domain_result = await self._backend.execute(
                plan=validated_plan.plan, 
                output_path=output_destination
            )
            
            duration = time.monotonic() - start_time
            
            if domain_result.status.value == "completed":
                return RenderExecutionResult.success(
                    duration_seconds=duration,
                    output_artifact_path=domain_result.rendered_output_location or output_destination
                )
            else:
                return RenderExecutionResult.failure(
                    duration_seconds=duration,
                    category=RenderFailureCategory.BACKEND_FAILURE,
                    message=domain_result.message or "Backend rendering failed.",
                    details=domain_result.rendering_metadata
                )
                
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
