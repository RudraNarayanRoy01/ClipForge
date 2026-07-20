from abc import ABC, abstractmethod

from src.editing.orchestration.commands import EditingExecutionCommand
from src.editing.orchestration.results import EditingExecutionResult


class IEditingOrchestrator(ABC):
    """
    Orchestration interface for the editing workflow.
    """

    @abstractmethod
    def execute(
        self,
        command: EditingExecutionCommand,
    ) -> EditingExecutionResult:
        """
        Coordinates the complete editing workflow.

        Receives an immutable orchestration command and produces 
        an immutable orchestration result containing the final RenderPlan.
        """
        pass
