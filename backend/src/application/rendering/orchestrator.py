from typing import Dict, Any, Optional
from datetime import datetime

from src.application.rendering.models import RenderJob, RenderJobStatus
from src.application.rendering.exceptions import InvalidRenderJobTransitionError, RenderJobValidationError
from src.application.rendering.interfaces import IRenderExecutionService
from src.application.execution_models import (
    ValidatedRenderPlan,
    RenderExecutionResult,
    RenderExecutionStatus,
)


class RenderJobOrchestrator:
    """
    Application-layer orchestration service for coordinating RenderJob execution.
    It delegates execution to IRenderExecutionService and remains stateless.
    It manages lifecycle validations, execution preparation, and result translations.
    """

    # Centralized legal transitions map
    _ALLOWED_TRANSITIONS = {
        RenderJobStatus.CREATED: {RenderJobStatus.VALIDATED},
        RenderJobStatus.VALIDATED: {RenderJobStatus.RUNNING},
        RenderJobStatus.RUNNING: {RenderJobStatus.COMPLETED, RenderJobStatus.FAILED},
    }

    def __init__(self, execution_service: IRenderExecutionService):
        """
        Args:
            execution_service: Abstraction for executing render plans.
        """
        self._execution_service = execution_service

    def validate_transition(self, current_status: RenderJobStatus, target_status: RenderJobStatus) -> None:
        """
        Validates if transitioning from current_status to target_status is allowed.
        Raises InvalidRenderJobTransitionError if not allowed.
        """
        allowed_targets = self._ALLOWED_TRANSITIONS.get(current_status, set())
        if target_status not in allowed_targets:
            raise InvalidRenderJobTransitionError(
                current_status=current_status.value,
                target_status=target_status.value,
                message=f"Transition from {current_status.name} to {target_status.name} is not allowed."
            )

    def validate_job(self, job: RenderJob) -> RenderJob:
        """
        Validates a CREATED job and transitions it to VALIDATED.
        
        Args:
            job: The RenderJob to validate.
            
        Returns:
            A new RenderJob instance in VALIDATED state.
            
        Raises:
            InvalidRenderJobTransitionError: If the job is not in CREATED state.
            RenderJobValidationError: If the job fails domain or application validations.
        """
        self.validate_transition(job.status, RenderJobStatus.VALIDATED)

        # In a real scenario, this is where we check if the plan itself is valid
        # For example, ensuring output paths are valid, inputs exist, etc.
        if not job.plan:
            raise RenderJobValidationError("RenderJob has no RenderPlan assigned.")
        
        if not job.plan.layers:
            raise RenderJobValidationError("RenderPlan must contain at least one layer.")

        return job.update_status(RenderJobStatus.VALIDATED)

    def prepare_execution(self, job: RenderJob) -> ValidatedRenderPlan:
        """
        Prepares the RenderJob for execution by wrapping its plan.
        """
        # Usually we would extract constraints, validate them again if necessary
        return ValidatedRenderPlan(
            plan=job.plan,
            validated_at=datetime.utcnow()
        )

    def translate_execution_result(self, job: RenderJob, result: RenderExecutionResult) -> RenderJob:
        """
        Translates a RenderExecutionResult into a new immutable RenderJob state.
        
        Args:
            job: The RenderJob currently in RUNNING state.
            result: The execution result from the backend.
            
        Returns:
            A new RenderJob instance in COMPLETED or FAILED state.
            
        Raises:
            InvalidRenderJobTransitionError: If the translation results in an illegal state change.
        """
        target_status = RenderJobStatus.FAILED
        if result.status == RenderExecutionStatus.COMPLETED:
            target_status = RenderJobStatus.COMPLETED
        
        self.validate_transition(job.status, target_status)
        return job.update_status(target_status)

    async def execute_job(
        self, 
        job: RenderJob, 
        output_destination: str, 
        execution_options: Optional[Dict[str, Any]] = None
    ) -> RenderJob:
        """
        Orchestrates the execution of a VALIDATED RenderJob.
        
        Args:
            job: A RenderJob in VALIDATED state.
            output_destination: Where the rendered output should be saved.
            execution_options: Optional execution configuration.
            
        Returns:
            A new RenderJob instance in COMPLETED or FAILED state.
            
        Raises:
            InvalidRenderJobTransitionError: If the job is not in VALIDATED state.
        """
        # 1. State transition validation to RUNNING
        self.validate_transition(job.status, RenderJobStatus.RUNNING)
        running_job = job.update_status(RenderJobStatus.RUNNING)
        
        # 2. Execution Preparation
        validated_plan = self.prepare_execution(running_job)
        
        # 3. Execution Delegation
        execution_result = await self._execution_service.execute_plan(
            validated_plan=validated_plan,
            output_destination=output_destination,
            execution_options=execution_options
        )
        
        # 4. Execution Result Translation
        return self.translate_execution_result(running_job, execution_result)
