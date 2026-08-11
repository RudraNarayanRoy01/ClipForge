from dataclasses import dataclass, field
from types import MappingProxyType
from datetime import datetime
from typing import Optional

from .runtime_execution_identity import RuntimeExecutionIdentity
from .runtime_execution_outcome import RuntimeExecutionOutcome

@dataclass(frozen=True)
class RuntimeExecutionResult:
    """
    Immutable terminal record produced after an execution attempt.
    """
    identity: RuntimeExecutionIdentity
    outcome: RuntimeExecutionOutcome
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    failure_reason: Optional[str] = None
    metadata: MappingProxyType[str, str] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self):
        # 1. duration_seconds >= 0
        if self.duration_seconds < 0.0:
            raise ValueError("Execution duration_seconds cannot be negative.")
            
        # 2. completed_at >= started_at
        if self.completed_at < self.started_at:
            raise ValueError("completed_at cannot be before started_at.")
            
        # 3. SUCCESS: failure_reason MUST be None
        if self.outcome == RuntimeExecutionOutcome.SUCCESS and self.failure_reason is not None:
            raise ValueError("SUCCESS outcome must not contain a failure_reason.")
            
        # 4. FAILED: failure_reason MUST be present and non-empty
        if self.outcome == RuntimeExecutionOutcome.FAILED:
            if not self.failure_reason or not str(self.failure_reason).strip():
                raise ValueError("FAILED outcome must contain a non-empty failure_reason.")
