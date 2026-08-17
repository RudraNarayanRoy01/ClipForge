from dataclasses import dataclass
from src.runtime.core.execution_target import ExecutionTarget

@dataclass(frozen=True)
class ExecutionAdmission:
    """
    Immutable representation of the Runtime's execution admission boundary.
    
    This contract establishes that an ExecutionTarget has been accepted and bound 
    for execution. It explicitly represents the handoff to execution infrastructure, 
    and does NOT represent the actual execution outcome or success state.
    """
    execution_target: ExecutionTarget
