from dataclasses import dataclass
from enum import Enum
from typing import Optional

from src.runtime.core.execution_target import ExecutionTarget

class ExecutionOutcome(str, Enum):
    """
    Authoritative semantic outcome of an execution attempt.
    """
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

@dataclass(frozen=True)
class ExecutionResult:
    """
    Immutable representation of the Runtime's execution outcome boundary.
    
    This establishes the provider-neutral, hardware-neutral, and scheduler-neutral 
    contract for the result of an execution.
    """
    execution_target: ExecutionTarget
    outcome: ExecutionOutcome
    error_message: Optional[str] = None
