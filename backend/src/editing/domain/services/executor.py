from abc import ABC, abstractmethod

from src.editing.domain.models.state import TimelineState
from src.editing.domain.models.transformation import TimelineOperation


class ITimelineOperationExecutor(ABC):
    """
    Architectural boundary for executing a single TimelineOperation against a TimelineState.
    Responsible for applying exactly one operation and returning an immutable new state.
    """

    @abstractmethod
    async def execute(self, state: TimelineState, operation: TimelineOperation) -> TimelineState:
        """
        Executes a single TimelineOperation on the provided TimelineState.
        Returns a new TimelineState, maintaining immutability.
        """
        pass
