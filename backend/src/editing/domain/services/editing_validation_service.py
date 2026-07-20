from abc import ABC, abstractmethod

from src.editing.domain.models.project import EditingProject
from src.editing.domain.models.plan import EditingPlan
from src.editing.domain.models.transformation import TimelineTransformationResult
from src.editing.domain.models.validation import ValidationResult


class IEditingValidationService(ABC):
    """
    Domain service interface for validating editing workflow outputs.
    Ensures that the generated plan and transformations satisfy project constraints.
    """

    @abstractmethod
    async def validate(
        self,
        project: EditingProject,
        plan: EditingPlan,
        transformation_result: TimelineTransformationResult,
    ) -> ValidationResult:
        """
        Validates the proposed editing decisions and timeline operations.
        
        Args:
            project: The original editing project context.
            plan: The editorial decisions made by the strategy.
            transformation_result: The resulting timeline operations.
            
        Returns:
            ValidationResult containing the validation outcome.
        """
        pass
