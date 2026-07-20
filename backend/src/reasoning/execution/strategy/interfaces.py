from abc import ABC, abstractmethod

from src.reasoning.execution.planner.models import ExecutionPlanDraft
from src.reasoning.execution.strategy.models import ExecutionStrategyResult


class IExecutionStrategy(ABC):
    """
    Defines the contract for the Execution Strategy Engine.
    Must transform an ExecutionPlanDraft into an ExecutionStrategyResult
    deterministically and purely.
    """

    @abstractmethod
    def generate_strategy(
        self, execution_plan_draft: ExecutionPlanDraft
    ) -> ExecutionStrategyResult:
        """
        Generates an execution strategy based on the given draft.

        Args:
            execution_plan_draft: The input draft from the Planner.

        Returns:
            ExecutionStrategyResult containing the editorial intent.
            
        Raises:
            StrategyGenerationError: If the strategy cannot be generated.
        """
        pass
