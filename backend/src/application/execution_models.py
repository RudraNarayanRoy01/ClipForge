from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.domain.render_plan import RenderPlan

@dataclass(frozen=True)
class ValidatedRenderPlan:
    """
    Represents a RenderPlan that has successfully passed validation.
    The execution layer must only accept this wrapped plan.
    """
    plan: RenderPlan
    validated_at: datetime


class RenderExecutionStatus(Enum):
    QUEUED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class RenderFailureCategory(Enum):
    """Neutral categorization of execution failures."""
    VALIDATION_REQUIRED = auto()  # Plan failed sanity checks at backend
    BACKEND_FAILURE = auto()      # Infrastructure/Rendering engine failure
    CANCELLED = auto()            # User/System cancelled
    INTERNAL_ERROR = auto()       # Bug or unexpected orchestration failure
    RESOURCE_EXHAUSTED = auto()   # OOM, timeout, disk space
    UNKNOWN = auto()              # Uncategorized failures


@dataclass(frozen=True)
class RenderExecutionRequest:
    """
    Backend-agnostic request to execute a rendering process.
    """
    validated_plan: ValidatedRenderPlan
    output_destination: str
    execution_options: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RenderExecutionDiagnostics:
    """
    Backend-agnostic diagnostics for execution failures.
    """
    category: RenderFailureCategory
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RenderExecutionResult:
    """
    Neutral execution result replacing backend-specific exceptions.
    """
    status: RenderExecutionStatus
    duration_seconds: float
    output_artifact_path: Optional[str] = None
    diagnostics: Optional[RenderExecutionDiagnostics] = None

    @classmethod
    def success(cls, duration_seconds: float, output_artifact_path: str) -> 'RenderExecutionResult':
        return cls(
            status=RenderExecutionStatus.COMPLETED,
            duration_seconds=duration_seconds,
            output_artifact_path=output_artifact_path
        )

    @classmethod
    def failure(cls, duration_seconds: float, category: RenderFailureCategory, message: str, details: Dict[str, Any] = None) -> 'RenderExecutionResult':
        return cls(
            status=RenderExecutionStatus.FAILED,
            duration_seconds=duration_seconds,
            diagnostics=RenderExecutionDiagnostics(
                category=category,
                message=message,
                details=details or {}
            )
        )
