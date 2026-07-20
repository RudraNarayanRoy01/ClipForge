from src.editing.domain.models.state import TimelineState
from src.editing.domain.models.transformation import TimelineTransformationResult
from src.editing.domain.services.timeline_execution_pipeline import ITimelineExecutionPipeline
from src.editing.domain.services.executor import ITimelineOperationExecutor


class DefaultTimelineExecutionPipeline(ITimelineExecutionPipeline):
    """
    Default implementation of the Timeline Execution Pipeline.
    Orchestrates the sequential execution of TimelineOperations by delegating
    to an ITimelineOperationExecutor.
    """

    def __init__(self, executor: ITimelineOperationExecutor):
        self._executor = executor

    async def execute(
        self, 
        state: TimelineState, 
        transformation_result: TimelineTransformationResult
    ) -> TimelineState:
        """
        Executes operations sequentially against the initial state.
        If no operations are present, returns the original state unchanged.
        Allows domain-specific execution exceptions to propagate naturally.
        """
        current_state = state
        
        for operation in transformation_result.operations:
            current_state = await self._executor.execute(current_state, operation)
            
        return current_state
