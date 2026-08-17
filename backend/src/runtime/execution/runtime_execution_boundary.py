from .execution_admission import ExecutionAdmission
from src.runtime.core.execution_target import ExecutionTarget


class RuntimeExecutionBoundary:
    """
    Authoritative execution entry boundary for the Runtime.
    
    Responsible for accepting an ExecutionTarget and establishing the execution 
    boundary, producing an ExecutionAdmission without performing provider-specific, 
    hardware-specific, or scheduler-specific execution itself.
    """

    def execute(self, target: ExecutionTarget) -> ExecutionAdmission:
        """
        Accept an ExecutionTarget and cross the execution boundary.
        
        Produces a deterministic, structural ExecutionAdmission, preserving the 
        exact target and identity semantics without claiming execution success.
        """
        if not isinstance(target, ExecutionTarget):
            raise TypeError("Execution target must be an instance of ExecutionTarget")
            
        return ExecutionAdmission(
            execution_target=target
        )
