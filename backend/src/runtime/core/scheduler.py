from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, Optional

from .selection import ProviderSelectionResult
from .providers import ProviderIdentity

class SchedulingStatus(Enum):
    """
    Architectural status of a scheduling outcome.
    
    This represents the operational decision outcome only.
    It must NOT represent execution success, provider health,
    runtime metrics, or optimization status.
    """
    SCHEDULED = auto()
    REJECTED_NO_ELIGIBLE_PROVIDER = auto()
    REJECTED_CONSTRAINTS = auto()


@dataclass(frozen=True)
class SchedulerRequest:
    """
    Immutable representation of a scheduling decision request.
    
    This object represents the intent to schedule architecturally eligible work.
    It MUST NOT contain:
    - execution state
    - retry information
    - runtime metrics
    - provider instances
    - optimization hints
    - execution progress
    - allocated resources
    
    After creation, this request is completely immutable.
    """
    selection_result: ProviderSelectionResult
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SchedulerResult:
    """
    Immutable representation of the scheduling outcome.
    
    This object represents the operational decision of WHERE and WHEN 
    eligible work should execute.
    
    It MUST NOT contain:
    - execution plans
    - execution graph
    - allocated hardware
    - execution state
    - provider instances
    - runtime metrics
    - optimization decisions
    - execution results
    
    Future Runtime layers should consume SchedulerResult rather than 
    extending or mutating it.
    """
    status: SchedulingStatus
    execution_placement: Optional[ProviderIdentity]
    execution_ordering: str
    scheduling_reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeScheduler:
    """
    The canonical architectural scheduling engine for the Runtime.
    
    This subsystem determines *where* and *when* architecturally eligible
    work should execute.
    
    It explicitly performs **Operational Decision Making** only.
    
    It MUST NOT determine:
    - how work executes
    - provider optimization
    - execution graph
    - dependency graph
    - retry strategy
    - workload orchestration
    - adaptive optimization
    
    It intentionally has NO ability to instantiate providers, execute providers,
    allocate hardware, monitor runtime, or orchestrate execution. Those responsibilities 
    belong to future Execution, Planning, and Optimization subsystems.
    """
    def __init__(self) -> None:
        pass

    def schedule(self, request: SchedulerRequest) -> SchedulerResult:
        """
        Evaluate scheduling constraints and determine execution placement and ordering
        based on the ProviderSelectionResult.
        """
        selection = request.selection_result
        
        if not selection.selected_provider_identity:
            return SchedulerResult(
                status=SchedulingStatus.REJECTED_NO_ELIGIBLE_PROVIDER,
                execution_placement=None,
                execution_ordering="IMMEDIATE",  # Fallback ordering
                scheduling_reasoning="Provider Selection yielded no eligible provider.",
                metadata={"selection_status": selection.status.name}
            )
            
        # In this foundation batch, scheduling is naive.
        # If the provider is eligible, it is scheduled for IMMEDIATE placement on that provider.
        return SchedulerResult(
            status=SchedulingStatus.SCHEDULED,
            execution_placement=selection.selected_provider_identity,
            execution_ordering="IMMEDIATE",
            scheduling_reasoning=f"Work scheduled for IMMEDIATE placement on provider '{selection.selected_provider_identity.identifier}'.",
            metadata={"selection_status": selection.status.name}
        )
