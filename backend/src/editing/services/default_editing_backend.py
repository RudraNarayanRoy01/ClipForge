from src.editing.domain.models.state import TimelineState
from src.editing.domain.models.transformation import TimelineTransformationResult
from src.editing.domain.models.execution import EditingExecutionResult
from src.editing.domain.services.editing_backend import IEditingBackend
from src.editing.domain.services.timeline_execution_pipeline import ITimelineExecutionPipeline
from src.editing.domain.services.timeline_validation_service import ITimelineValidationService


class DefaultEditingBackend(IEditingBackend):
    """
    Default implementation of IEditingBackend.
    
    Orchestrates execution and validation by delegating to 
    ITimelineExecutionPipeline and ITimelineValidationService.
    Does not contain execution or validation logic itself.
    """

    def __init__(
        self,
        execution_pipeline: ITimelineExecutionPipeline,
        validation_service: ITimelineValidationService,
    ):
        """
        Initializes the DefaultEditingBackend with required services.
        
        Args:
            execution_pipeline: The service responsible for timeline execution.
            validation_service: The service responsible for timeline validation.
        """
        self._execution_pipeline = execution_pipeline
        self._validation_service = validation_service

    async def execute(
        self,
        initial_timeline_state: TimelineState,
        transformation_result: TimelineTransformationResult
    ) -> EditingExecutionResult:
        """
        Delegates execution to the execution pipeline and subsequent validation 
        to the validation service, returning a combined EditingExecutionResult.
        
        Args:
            initial_timeline_state: The initial state of the timeline.
            transformation_result: The transformation to execute.
            
        Returns:
            An EditingExecutionResult containing the final timeline state and validation outcome.
        """
        # 1. Delegate execution to ITimelineExecutionPipeline
        final_state = await self._execution_pipeline.execute(
            state=initial_timeline_state,
            transformation_result=transformation_result
        )
        
        # 2. Delegate validation to ITimelineValidationService
        validation_result = self._validation_service.validate(timeline_state=final_state)
        
        # 3. Return a single immutable EditingExecutionResult
        return EditingExecutionResult(
            state=final_state,
            validation_result=validation_result
        )
