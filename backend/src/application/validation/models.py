from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum, auto


class ValidationSeverity(Enum):
    """
    Indicates the severity of a validation issue.
    """
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass(frozen=True)
class RenderValidationIssue:
    """
    Represents a specific issue found during validation.
    Immutable representation of a structural or logical flaw.
    """
    severity: ValidationSeverity
    message: str
    context_path: Optional[str] = None
    
    @classmethod
    def error(cls, message: str, context_path: Optional[str] = None) -> 'RenderValidationIssue':
        return cls(severity=ValidationSeverity.ERROR, message=message, context_path=context_path)

    @classmethod
    def warning(cls, message: str, context_path: Optional[str] = None) -> 'RenderValidationIssue':
        return cls(severity=ValidationSeverity.WARNING, message=message, context_path=context_path)
        
    @classmethod
    def info(cls, message: str, context_path: Optional[str] = None) -> 'RenderValidationIssue':
        return cls(severity=ValidationSeverity.INFO, message=message, context_path=context_path)


@dataclass(frozen=True)
class RenderValidationResult:
    """
    Aggregate result of a validation pass.
    """
    issues: List[RenderValidationIssue] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """
        A plan is only considered invalid if there are ERROR severity issues.
        """
        return not any(issue.severity == ValidationSeverity.ERROR for issue in self.issues)
    
    @property
    def errors(self) -> List[RenderValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]
        
    @property
    def warnings(self) -> List[RenderValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]

    @property
    def infos(self) -> List[RenderValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.INFO]
