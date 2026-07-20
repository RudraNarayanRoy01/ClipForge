from dataclasses import dataclass

from src.editing.domain.models.state import TimelineState
from src.editing.domain.models.validation import ValidationResult


@dataclass(frozen=True)
class EditingExecutionResult:
    """
    The canonical outcome of executing a timeline transformation.
    
    Contains the resulting timeline state and the validation outcome.
    Does not include rendering information, export information, or playback information.
    Maintains immutability.
    """
    state: TimelineState
    validation_result: ValidationResult
