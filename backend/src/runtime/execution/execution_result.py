from dataclasses import dataclass
from typing import Optional

from src.runtime.core.execution_target import ExecutionTarget


@dataclass(frozen=True)
class ExecutionResult:
    """
    Immutable representation of the Runtime's execution outcome boundary.
    
    This establishes the provider-neutral, hardware-neutral, and scheduler-neutral 
    contract for the result of an execution.
    """
    execution_target: ExecutionTarget
    is_success: bool
    error_message: Optional[str] = None
