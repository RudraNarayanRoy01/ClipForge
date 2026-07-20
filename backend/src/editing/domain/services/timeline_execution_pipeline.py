from abc import ABC, abstractmethod

from src.editing.domain.models.state import TimelineState
from src.editing.domain.models.transformation import TimelineTransformationResult


class ITimelineExecutionPipeline(ABC):
    """
    Architectural boundary for the Timeline Execution Pipeline.
    Responsible for orchestrating the execution of an entire 
    TimelineTransformationResult against a TimelineState.
    """

    @abstractmethod
    async def execute(
        self, 
        state: TimelineState, 
        transformation_result: TimelineTransformationResult
    ) -> TimelineState:
        """
        Sequentially executes every TimelineOperation contained within the 
        TimelineTransformationResult against the initial TimelineState.
        Returns the final TimelineState.
        """
        pass
