from abc import ABC, abstractmethod

from src.reasoning.execution.models import ExecutionInput
from .models import ExecutionPlanDraft


class IExecutionPlanner(ABC):
    """
    Interface for deterministic Execution Planners.
    Implementations must transform an immutable ExecutionInput into an
    ExecutionPlanDraft without making business decisions, validating plans,
    or constructing ExecutionPlans.
    """

    @abstractmethod
    def create_execution_draft(self, execution_input: ExecutionInput) -> ExecutionPlanDraft:
        """
        Transforms ExecutionInput into a deterministic ExecutionPlanDraft.
        """
        pass
