import uuid
from abc import ABC, abstractmethod

from src.reasoning.execution.models import ExecutionInput, ExecutionPlan


class IExecutionService(ABC):
    """
    Interface for the Execution Service.
    Responsible solely for orchestrating the execution pipeline.
    It does not implement planning, strategy, validation, or composition logic.
    """

    @abstractmethod
    def generate_execution_plan(
        self,
        execution_input: ExecutionInput,
        plan_id: uuid.UUID,
    ) -> ExecutionPlan:
        """
        Orchestrates Planner, Strategy, Validation, and Composer to generate an ExecutionPlan.

        Args:
            execution_input: The immutable input context.
            plan_id: The identifier for the plan, supplied by the upstream caller.

        Returns:
            ExecutionPlan: The composed aggregate.
        """
        pass
