from abc import ABC, abstractmethod

from src.reasoning.execution.planner.models import ExecutionPlanDraft
from src.reasoning.execution.strategy.models import ExecutionStrategyResult
from src.reasoning.execution.validation.models import ExecutionValidationResult


class IExecutionValidation(ABC):
    """
    Interface for the Execution Validation Engine.
    Follows the Open/Closed Principle.
    """
    
    @abstractmethod
    def validate_execution(
        self,
        draft: ExecutionPlanDraft,
        strategy: ExecutionStrategyResult
    ) -> ExecutionValidationResult:
        """
        Validates the execution outputs for structural consistency, completeness, and compatibility.
        Does not repair or modify the inputs.
        
        Args:
            draft: The immutable output from the Planner.
            strategy: The immutable output from the Strategy Engine.
            
        Returns:
            ExecutionValidationResult: The validation findings.
        """
        pass
