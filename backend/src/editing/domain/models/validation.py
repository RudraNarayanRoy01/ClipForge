from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class ValidationResult:
    """
    Result of validating the editorial intent and timeline transformations.
    Contains validation status and any resulting errors or warnings.
    """
    is_valid: bool
    errors: Tuple[str, ...]
