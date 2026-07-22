from typing import Dict, Any, Optional, List
from datetime import datetime

from src.application.rendering.models import RenderJob, RenderJobStatus, RenderProgress
from src.application.rendering.exceptions import InvalidRenderJobTransitionError, RenderJobValidationError
from src.application.rendering.interfaces import (
    IRenderExecutionService,
    IRenderProgressObserver,
    IRenderTelemetryObserver
)
from src.application.execution_models import (
    ValidatedRenderPlan,
    RenderExecutionResult,
    RenderExecutionStatus,
)
from src.application.rendering.telemetry import RenderExecutionEvent, RenderEventType
from src.application.rendering.session import RenderExecutionSession


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
        RenderJobStatus.RUNNING: {RenderJobStatus.COMPLETED, RenderJobStatus.FAILED, RenderJobStatus.CANCELLED},
    }

    def __init__(self, execution_service: IRenderExecutionService):
        """
        Args:
            execution_service: Abstraction for executing render plans.
        """
        self._execution_service = execution_service
        self._progress_observers: List[IRenderProgressObserver] = []
        self._telemetry_observers: List[IRenderTelemetryObserver] = []

    def register_progress_observer(self, observer: IRenderProgressObserver) -> None:
        self._progress_observers.append(observer)

    def register_telemetry_observer(self, observer: IRenderTelemetryObserver) -> None:
        self._telemetry_observers.append(observer)

    def _notify_progress(self, progress: RenderProgress) -> None:
        for observer in self._progress_observers:
            observer.on_progress(progress)

    def _notify_telemetry(self, event: RenderExecutionEvent) -> None:
        for observer in self._telemetry_observers:
            observer.on_event(event)

    def _evolve_session(
        self, 
        session: RenderExecutionSession, 
        event: Optional[RenderExecutionEvent] = None, 
        job: Optional[RenderJob] = None, 
        progress: Optional[RenderProgress] = None
    ) -> RenderExecutionSession:
        """
        Centralized session evolution.
        Ensures a completely new immutable session is created before notifying observers,
        so observers never see a partially updated state.
        """
        new_session = session
        if job:
            new_session = new_session.with_job(job)
        if event:
            new_session = new_session.with_event(event)
        if progress:
            new_session = new_session.with_progress(progress)
            
        # Notify only after new immutable session is fully created
        if progress:
            self._notify_progress(progress)
        if event:
            self._notify_telemetry(event)
            
        return new_session

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

    def initialize_session(self, job: RenderJob) -> RenderExecutionSession:
        """
        Creates the initial session and fires JOB_CREATED telemetry.
        """
        session = RenderExecutionSession.initialize(job)
        event = RenderExecutionEvent.create(
            job_id=job.id,
            event_type=RenderEventType.JOB_CREATED,
            message="RenderJob created and session initialized."
        )
        return self._evolve_session(session, event=event)

    def validate_job(self, session: RenderExecutionSession) -> RenderExecutionSession:
        """
        Validates a CREATED job and transitions it to VALIDATED.
        
        Args:
            session: The RenderExecutionSession to validate.
            
        Returns:
            A new RenderExecutionSession in VALIDATED state.
            
        Raises:
            InvalidRenderJobTransitionError: If the job is not in CREATED state.
            RenderJobValidationError: If the job fails domain or application validations.
        """
        job = session.job
        self.validate_transition(job.status, RenderJobStatus.VALIDATED)

        if not job.plan:
            raise RenderJobValidationError("RenderJob has no RenderPlan assigned.")
        
        if not job.plan.layers:
            raise RenderJobValidationError("RenderPlan must contain at least one layer.")

        new_job = job.update_status(RenderJobStatus.VALIDATED)
        event = RenderExecutionEvent.create(
            job_id=job.id,
            event_type=RenderEventType.VALIDATED,
            message="RenderJob validated successfully."
        )
        return self._evolve_session(session, event=event, job=new_job)

    def prepare_execution(self, job: RenderJob) -> ValidatedRenderPlan:
        """
        Prepares the RenderJob for execution by wrapping its plan.
        """
        return ValidatedRenderPlan(
            plan=job.plan,
            validated_at=datetime.utcnow()
        )

    def translate_execution_result(self, session: RenderExecutionSession, result: RenderExecutionResult) -> RenderExecutionSession:
        """
        Translates a RenderExecutionResult into a new immutable RenderExecutionSession state.
        
        Args:
            session: The session currently in RUNNING state.
            result: The execution result from the backend.
            
        Returns:
            A new RenderExecutionSession instance in COMPLETED, FAILED, or CANCELLED state.
            
        Raises:
            InvalidRenderJobTransitionError: If the translation results in an illegal state change.
        """
        job = session.job
        target_status = RenderJobStatus.FAILED
        event_type = RenderEventType.FAILED
        message = "Render execution failed."
        metadata = {}

        if result.status == RenderExecutionStatus.COMPLETED:
            target_status = RenderJobStatus.COMPLETED
            event_type = RenderEventType.COMPLETED
            message = "Render execution completed successfully."
        elif result.status == RenderExecutionStatus.CANCELLED:
            target_status = RenderJobStatus.CANCELLED
            event_type = RenderEventType.CANCELLED
            message = "Render execution was cancelled."
            
        if result.diagnostics:
            metadata["reason"] = result.diagnostics.message
            metadata["category"] = result.diagnostics.category.name
            message = result.diagnostics.message

        self.validate_transition(job.status, target_status)
        new_job = job.update_status(target_status)
        event = RenderExecutionEvent.create(
            job_id=job.id,
            event_type=event_type,
            message=message,
            metadata=metadata
        )
        return self._evolve_session(session, event=event, job=new_job)

    async def execute_job(
        self, 
        session: RenderExecutionSession, 
        output_destination: str, 
        execution_options: Optional[Dict[str, Any]] = None
    ) -> RenderExecutionSession:
        """
        Orchestrates the execution of a VALIDATED session.
        
        Args:
            session: A session in VALIDATED state.
            output_destination: Where the rendered output should be saved.
            execution_options: Optional execution configuration.
            
        Returns:
            A new RenderExecutionSession instance in COMPLETED or FAILED state.
            
        Raises:
            InvalidRenderJobTransitionError: If the job is not in VALIDATED state.
        """
        job = session.job
        # 1. State transition validation to RUNNING
        self.validate_transition(job.status, RenderJobStatus.RUNNING)
        new_job = job.update_status(RenderJobStatus.RUNNING)
        
        start_event = RenderExecutionEvent.create(
            job_id=job.id,
            event_type=RenderEventType.STARTED,
            message="Render execution started."
        )
        current_session = self._evolve_session(session, event=start_event, job=new_job)
        
        # 2. Execution Preparation
        validated_plan = self.prepare_execution(new_job)
        
        opts = dict(execution_options) if execution_options else {}
        
        # 3. Execution Delegation
        # We treat progress_callback strictly as an internal adapter.
        def internal_progress_callback(progress: RenderProgress) -> None:
            nonlocal current_session
            current_session = self._evolve_session(current_session, progress=progress)
            
        opts["progress_callback"] = internal_progress_callback

        execution_result = await self._execution_service.execute_plan(
            validated_plan=validated_plan,
            output_destination=output_destination,
            execution_options=opts
        )
        
        # 4. Execution Result Translation
        return self.translate_execution_result(current_session, execution_result)
