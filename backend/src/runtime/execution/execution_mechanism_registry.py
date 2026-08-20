from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Dict, Tuple, Type, Any
from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.core.execution_workload import ExecutionWorkload
from src.runtime.execution.execution_result import ExecutionOutcome

TWorkload = TypeVar("TWorkload", bound=ExecutionWorkload)

class AbstractExecutionMechanism(Generic[TWorkload], ABC):
    """
    Minimal, provider-neutral execution mechanism dependency.
    
    Generic over the specific TWorkload it executes.
    Responsible for interpreting provider/environment-specific failures and 
    translating expected execution failures into the neutral execution-mechanism 
    contract: (ExecutionOutcome, error_message).
    """
    @abstractmethod
    def execute(self, target: ExecutionTarget, workload: TWorkload) -> Tuple[ExecutionOutcome, Optional[str]]:
        ...

@dataclass(frozen=True)
class MechanismRegistration:
    """
    Metadata binding a mechanism to its expected workload type.
    """
    expected_workload_type: Type[ExecutionWorkload]
    mechanism: AbstractExecutionMechanism[Any]

class MechanismResolutionError(Exception):
    """Raised when no compatible mechanism can be found."""
    pass

class ExecutionMechanismRegistry:
    """
    Registry for execution mechanisms. Injected into ExecutionEngine.
    """
    def __init__(self) -> None:
        self._registry: Dict[Tuple[str, str], MechanismRegistration] = {}
        
    def register(self, provider_id: str, capability_id: str, expected_type: Type[ExecutionWorkload], mechanism: AbstractExecutionMechanism[Any]) -> None:
        """Register a mechanism for a given provider and capability."""
        key = (provider_id, capability_id)
        if key in self._registry:
            raise ValueError(f"Mechanism for provider '{provider_id}' and capability '{capability_id}' already registered.")
        self._registry[key] = MechanismRegistration(expected_type, mechanism)
        
    def resolve(self, provider_id: str, capability_id: str) -> MechanismRegistration:
        """Resolve a MechanismRegistration by provider_id and capability_id."""
        key = (provider_id, capability_id)
        if key not in self._registry:
            raise MechanismResolutionError(f"No mechanism registered for provider '{provider_id}' and capability '{capability_id}'.")
        return self._registry[key]
