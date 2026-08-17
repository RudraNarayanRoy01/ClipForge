from typing import Protocol, TypeVar, runtime_checkable
from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.execution_workload import ExecutionWorkload

class WorkloadNormalizationError(Exception):
    """
    Raised when an opaque intent payload cannot be normalized into a truthful ExecutionWorkload.
    """
    pass

TWorkload = TypeVar("TWorkload", bound=ExecutionWorkload)

@runtime_checkable
class WorkloadNormalizer(Protocol[TWorkload]):
    """
    The capability-owned normalization boundary.
    
    Transforms the abstract intent payload into a validated execution workload.
    
    Must NOT:
    - select providers
    - select hardware
    - schedule work
    - execute work
    - call provider APIs
    """
    
    def normalize(self, intent: ExecutionIntent) -> TWorkload:
        """
        Normalize an ExecutionIntent into a typed ExecutionWorkload.
        
        Args:
            intent: The abstract capability intent.
            
        Returns:
            The normalized, capability-specific execution workload.
            
        Raises:
            WorkloadNormalizationError: If the payload cannot be safely normalized.
        """
        ...
