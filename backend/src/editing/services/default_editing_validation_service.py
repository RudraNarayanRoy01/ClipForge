from src.editing.domain.models.plan import EditingPlan
from src.editing.domain.models.project import EditingProject
from src.editing.domain.models.transformation import TimelineTransformationResult
from src.editing.domain.models.validation import ValidationResult
from src.editing.domain.services.editing_validation_service import IEditingValidationService


class DefaultEditingValidationService(IEditingValidationService):
    """
    The canonical Validation layer for the editing subsystem.
    
    This service independently evaluates editing plans and timeline transformations
    against the project's constraints. It is an independent capability consumed by 
    the Editing Pipeline, ensuring validation logic remains strictly isolated from 
    workflow orchestration.
    """

    async def validate(
        self,
        project: EditingProject,
        plan: EditingPlan,
        transformation_result: TimelineTransformationResult,
    ) -> ValidationResult:
        """
        Validates the proposed editing decisions and operations.
        
        This default implementation currently returns a successful result.
        Concrete business rules and heuristics belong here.
        """
        return ValidationResult(is_valid=True, errors=())
