from typing import Protocol, Optional
from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.execution.execution_admission import ExecutionAdmission
from src.runtime.execution.execution_result import ExecutionResult


class AbstractExecutionMechanism(Protocol):
    """
    Minimal, provider-neutral execution mechanism dependency.
    
    Responsible for interpreting provider/environment-specific failures and 
    translating expected execution failures into the neutral execution-mechanism 
    contract: (False, error_message).
    
    Unexpected programming or infrastructure errors (e.g., TypeError) should be 
    allowed to propagate outward naturally.
    """
    def execute_target(self, target: ExecutionTarget) -> tuple[bool, Optional[str]]:
        ...


class ExecutionEngine:
    """
    Authoritative ExecutionEngine for the certified Runtime execution path.
    
    Responsible for accepting an ExecutionAdmission, extracting the target,
    invoking the abstract execution mechanism, and constructing a truthful 
    ExecutionResult from the mechanism's outcome.
    
    It performs NO scheduling, hardware mapping, or provider-specific logic.
    """
    def __init__(self, execution_mechanism: AbstractExecutionMechanism) -> None:
        self._execution_mechanism = execution_mechanism

    def execute(self, admission: ExecutionAdmission) -> ExecutionResult:
        """
        Executes the admitted target using the injected execution mechanism.
        
        Extracts the exact target identity and passes it to the mechanism.
        Success is derived STRICTLY from the mechanism's boolean outcome,
        not from the existence of the admission itself.
        """
        if not isinstance(admission, ExecutionAdmission):
            raise TypeError("admission must be an instance of ExecutionAdmission")
            
        target = admission.execution_target
        
        # We do NOT use 'except Exception:' here.
        # Expected execution failures are handled gracefully by the mechanism
        # and returned as a (False, error_message) tuple.
        # Unexpected infrastructure/programming errors will propagate naturally.
        is_success, error_message = self._execution_mechanism.execute_target(target)
        
        return ExecutionResult(
            execution_target=target,
            is_success=is_success,
            error_message=error_message
        )
