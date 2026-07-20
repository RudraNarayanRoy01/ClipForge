from dataclasses import dataclass

from src.editing.domain.models.plan import EditingPlan
from src.editing.domain.models.transformation import TimelineTransformationResult
from src.editing.domain.models.validation import ValidationResult


@dataclass(frozen=True)
class EditingPipelineResult:
    """
    The canonical output of the Editing Pipeline (Sprint 5.1).
    
    Contains the resulting editing plan, the timeline transformation 
    results, and the validation outcome. Designed to be extensible 
    for future metadata such as diagnostics, execution metrics, 
    and optimization hints without changing the public API.
    """
    plan: EditingPlan
    transformation_result: TimelineTransformationResult
    validation_result: ValidationResult
