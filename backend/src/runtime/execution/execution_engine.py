from typing import Protocol, Optional
from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.core.execution_workload import ExecutionWorkload
from src.runtime.execution.execution_admission import ExecutionAdmission
from src.runtime.execution.execution_result import ExecutionResult
from .execution_mechanism_registry import ExecutionMechanismRegistry

class WorkloadCompatibilityError(Exception):
    """Raised when an execution workload fails runtime type compatibility validation."""
    pass

class ExecutionEngine:
    """
    Authoritative ExecutionEngine for the certified Runtime execution path.
    
    Responsible for accepting an ExecutionAdmission, extracting the target and workload,
    resolving the execution mechanism via registry, verifying workload compatibility,
    invoking the execution mechanism, and constructing a truthful ExecutionResult.
    
    It performs NO scheduling, hardware mapping, or provider-specific logic.
    """
    def __init__(self, mechanism_registry: ExecutionMechanismRegistry) -> None:
        self._mechanism_registry = mechanism_registry

    def execute(self, admission: ExecutionAdmission) -> ExecutionResult:
        """
        Executes the admitted target and workload using the resolved execution mechanism.
        
        Resolves mechanism via (provider_id, capability_id), guarantees type compatibility
        at runtime, and delegates execution.
        """
        if not isinstance(admission, ExecutionAdmission):
            raise TypeError("admission must be an instance of ExecutionAdmission")
            
        target = admission.execution_target
        workload = admission.execution_workload

        # 1. Resolve mechanism
        registration = self._mechanism_registry.resolve(
            target.provider,
            workload.capability_id
        )

        # 2. Generic runtime compatibility validation
        if not isinstance(workload, registration.expected_workload_type):
            raise WorkloadCompatibilityError(
                f"Workload of type {type(workload).__name__} is incompatible with "
                f"expected type {registration.expected_workload_type.__name__}."
            )
        
        # 3. Delegate execution
        # Expected execution failures are handled gracefully by the mechanism
        # and returned as a (False, error_message) tuple.
        is_success, error_message = registration.mechanism.execute(target, workload)
        
        return ExecutionResult(
            execution_target=target,
            is_success=is_success,
            error_message=error_message
        )
