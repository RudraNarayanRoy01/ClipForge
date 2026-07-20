from abc import ABC, abstractmethod

from src.editing.domain.models.state import TimelineState
from src.editing.domain.models.transformation import TimelineTransformationResult
from src.editing.domain.models.execution import EditingExecutionResult


class IEditingBackend(ABC):
    """
    Public backend-facing entry point for the Timeline Execution Engine.
    
    Coordinates the editing workflow by orchestrating timeline execution 
    and validation. Acts purely as an orchestration façade.
    It does not execute operations or validate timelines itself.
    """

    @abstractmethod
    async def execute(
        self,
        initial_timeline_state: TimelineState,
        transformation_result: TimelineTransformationResult
    ) -> EditingExecutionResult:
        """
        Coordinates the execution of a timeline transformation and its subsequent validation.
        
        Args:
            initial_timeline_state: The initial state of the timeline.
            transformation_result: The transformation to execute.
            
        Returns:
            An EditingExecutionResult containing the final state and validation outcome.
        """
        pass
