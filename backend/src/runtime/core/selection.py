from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, List, Optional

from .capabilities import RuntimeCapabilityRegistry
from .providers import RuntimeProviderRegistry, ProviderIdentity
from .hardware import RuntimeHardwareDiscovery

class ProviderSelectionStatus(Enum):
    """
    Architectural status of a provider selection evaluation.
    
    Selection status represents architectural outcomes only.
    It must never represent execution state, network errors,
    or runtime exceptions.
    """
    SUCCESS = auto()
    NO_PROVIDER_FOUND = auto()
    CAPABILITY_NOT_SUPPORTED = auto()
    HARDWARE_NOT_AVAILABLE = auto()
    CONSTRAINTS_NOT_SATISFIED = auto()


@dataclass(frozen=True)
class ProviderSelectionRequest:
    """
    Immutable representation of an architectural provider selection request.
    
    This object represents architectural intent only. It does NOT contain:
    - execution state
    - runtime metrics
    - scheduler hints
    - optimization preferences
    - benchmark data
    - provider health
    - utilization
    
    After creation, this request is completely immutable.
    """
    requested_capability_id: str
    provider_constraints: List[str] = field(default_factory=list)
    hardware_constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderSelectionResult:
    """
    Immutable representation of the architectural outcome of provider evaluation.
    
    This object represents only the architectural eligibility matching. 
    It MUST NOT contain:
    - execution plans
    - scheduling decisions
    - runtime metrics
    - provider instances
    - model handles
    - allocated hardware
    - optimization scores
    
    Future Runtime layers should consume ProviderSelectionResult rather than 
    extending or mutating it.
    """
    selected_provider_identity: Optional[ProviderIdentity]
    status: ProviderSelectionStatus
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeProviderSelection:
    """
    The canonical architectural matching engine for Runtime Providers.
    
    This subsystem determines *which Provider is architecturally eligible* 
    to satisfy a capability request.
    
    It explicitly performs **Architectural Decision Making** only.
    
    It MUST NOT determine:
    - where execution occurs
    - when execution occurs
    - how execution occurs
    - runtime optimization
    - workload scheduling
    - provider execution
    
    It intentionally has NO ability to instantiate providers, benchmark performance,
    reserve hardware, or execute workloads. Those responsibilities belong to 
    future Execution, Planning, and Scheduling subsystems.
    """
    def __init__(
        self,
        capability_registry: RuntimeCapabilityRegistry,
        provider_registry: RuntimeProviderRegistry,
        hardware_discovery: RuntimeHardwareDiscovery
    ) -> None:
        self._capability_registry = capability_registry
        self._provider_registry = provider_registry
        self._hardware_discovery = hardware_discovery

    def select_provider(self, request: ProviderSelectionRequest) -> ProviderSelectionResult:
        """
        Evaluate architectural eligibility based on the requested capability
        and constraints.
        
        This evaluation is strictly architectural and does NOT consider 
        provider health, system load, or hardware utilization.
        """
        # Validate that the capability is known to the Runtime
        try:
            self._capability_registry.get_descriptor(request.requested_capability_id)
        except KeyError:
            return ProviderSelectionResult(
                selected_provider_identity=None,
                status=ProviderSelectionStatus.CAPABILITY_NOT_SUPPORTED,
                reasoning=f"Capability '{request.requested_capability_id}' is not known to the Runtime Capability Registry."
            )

        # Enumerate all providers to find a match
        providers = self._provider_registry.enumerate_providers()
        
        eligible_providers = []
        for reg in providers:
            descriptor = reg.descriptor
            
            # Check capability match
            if request.requested_capability_id not in descriptor.supported_capability_ids:
                continue
                
            # Check explicit provider constraints (if any)
            if request.provider_constraints:
                if descriptor.identity.identifier not in request.provider_constraints:
                    continue
                    
            # Check explicit hardware constraints (if any)
            if request.hardware_constraints:
                # Naive architectural check: Does the provider claim to support the hardware?
                meets_hardware_constraints = True
                for hw_req in request.hardware_constraints:
                    if hw_req not in descriptor.supported_resource_ids:
                        meets_hardware_constraints = False
                        break
                
                if not meets_hardware_constraints:
                    continue
                    
            eligible_providers.append(descriptor.identity)
            
        if not eligible_providers:
            # Differentiate between no provider existing vs constraints eliminating them
            if not request.provider_constraints and not request.hardware_constraints:
                return ProviderSelectionResult(
                    selected_provider_identity=None,
                    status=ProviderSelectionStatus.NO_PROVIDER_FOUND,
                    reasoning=f"No provider registered that supports capability '{request.requested_capability_id}'."
                )
            else:
                return ProviderSelectionResult(
                    selected_provider_identity=None,
                    status=ProviderSelectionStatus.CONSTRAINTS_NOT_SATISFIED,
                    reasoning=f"Providers exist for capability '{request.requested_capability_id}', but none satisfy the requested constraints."
                )
                
        # For this foundation batch, simply return the first architecturally eligible provider.
        return ProviderSelectionResult(
            selected_provider_identity=eligible_providers[0],
            status=ProviderSelectionStatus.SUCCESS,
            reasoning=f"Provider '{eligible_providers[0].identifier}' is architecturally eligible."
        )
