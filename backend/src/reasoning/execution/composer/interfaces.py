import uuid
from abc import ABC, abstractmethod

from src.reasoning.execution.planner.models import ExecutionPlanDraft
from src.reasoning.execution.strategy.models import ExecutionStrategyResult
from src.reasoning.execution.validation.models import ExecutionValidationResult
from src.reasoning.execution.models import ExecutionPlan


class IExecutionComposer(ABC):
    """
    Interface for the Execution Composer.
    The Composer is the sole owner responsible for constructing the immutable ExecutionPlan aggregate.
    It does not perform planning, validation, editing, or orchestration.
    """

    @abstractmethod
    def compose_execution_plan(
        self,
        plan_id: uuid.UUID,
        draft: ExecutionPlanDraft,
        strategy: ExecutionStrategyResult,
        validation: ExecutionValidationResult,
    ) -> ExecutionPlan:
        """
        Constructs an ExecutionPlan from immutable outputs of the Planner, Strategy, and Validation components.
        
        Args:
            plan_id: The unique identifier for the execution plan, supplied from an upstream source.
            draft: The deterministic output of the Execution Planner.
            strategy: The deterministic output of the Execution Strategy Engine.
            validation: The deterministic output of the Execution Validation Engine.
            
        Returns:
            ExecutionPlan: The fully constructed, immutable ExecutionPlan aggregate.
        """
        pass
