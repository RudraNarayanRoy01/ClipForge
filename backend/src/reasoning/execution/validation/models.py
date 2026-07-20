from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple


class ValidationSeverity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ValidationCategory(Enum):
    STRUCTURAL = "STRUCTURAL"
    COMPLETENESS = "COMPLETENESS"
    COMPATIBILITY = "COMPATIBILITY"


@dataclass(frozen=True)
class ValidationIssue:
    """
    Represents a specific validation finding.
    Does not attempt to resolve the issue.
    """
    message: str
    severity: ValidationSeverity
    category: ValidationCategory


@dataclass(frozen=True)
class ExecutionValidationResult:
    """
    Represents the deterministic output of the Execution Validation Engine.
    Produces validation findings without modifying previous outputs.
    """
    is_valid: bool
    issues: Tuple[ValidationIssue, ...] = field(default_factory=tuple)
