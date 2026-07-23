from abc import ABC, abstractmethod

from src.editing.orchestration.commands import EditingExecutionCommand
from src.editing.orchestration.results import EditingOrchestrationResult


class IEditingOrchestrator(ABC):
    """
    Orchestration interface for the editing workflow.
    """

    @abstractmethod
    async def execute(
        self,
        command: EditingExecutionCommand,
    ) -> EditingOrchestrationResult:
        """
        Coordinates the complete editing workflow.

        Receives an immutable orchestration command and produces 
        an immutable orchestration result containing the final RenderPlan.
        """
        pass
