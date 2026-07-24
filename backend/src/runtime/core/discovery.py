from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime


class ResourceCategory(Enum):
    """
    Architectural taxonomy for discovered resources.
    
    Currently, only CAPABILITY resources are expected to exist.
    Other categories (PROVIDER, HARDWARE, MODEL, SERVICE, INFRASTRUCTURE)
    are strictly reserved for future architectural expansion.
    """
    CAPABILITY = auto()
    PROVIDER = auto()
    HARDWARE = auto()
    MODEL = auto()
    SERVICE = auto()
    INFRASTRUCTURE = auto()


@dataclass(frozen=True)
class ResourceDescriptor:
    """
    An immutable definition of an architectural resource.
    
    This descriptor represents a discovered resource conceptually.
    It intentionally avoids provider-specific or execution-state fields.
    Once created, its properties cannot be mutated.
    """
    identifier: str
    category: ResourceCategory
    display_name: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DiscoveryResult:
    """
    An immutable payload representing the result of a discovery operation.
    
    This separates the immutable architectural resource definition (ResourceDescriptor)
    from the discovery event. It MUST NOT mutate the ResourceDescriptor.
    """
    descriptor: ResourceDescriptor
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    source: str = "RuntimeResourceDiscovery"


class RuntimeResourceDiscovery:
    """
    The canonical architectural subsystem for discovering Runtime resources.
    
    Responsibilities:
    - Discover Runtime resources.
    - Enumerate discovered resources.
    - Expose immutable DiscoveryResults.
    - Validate duplicate discoveries.
    - Remain completely provider independent.
    
    It explicitly MUST NOT:
    - Resolve or instantiate providers.
    - Load models.
    - Schedule execution.
    - Benchmark hardware.
    - Execute AI workloads.
    - Select providers.
    
    Owned exclusively by the RuntimeContext. Future systems should access discovery
    through the RuntimeContext.
    """
    def __init__(self) -> None:
        self._results: Dict[str, DiscoveryResult] = {}

    def discover(self, descriptor: ResourceDescriptor, source: str = "RuntimeResourceDiscovery") -> DiscoveryResult:
        """
        Record a newly discovered resource.
        
        Raises ValueError if a resource with the same identifier has already been discovered.
        Returns an immutable DiscoveryResult.
        """
        if descriptor.identifier in self._results:
            raise ValueError(f"Resource '{descriptor.identifier}' has already been discovered.")
        
        result = DiscoveryResult(descriptor=descriptor, source=source)
        self._results[descriptor.identifier] = result
        return result

    def get_discovery_result(self, identifier: str) -> DiscoveryResult:
        """Retrieve the immutable discovery result for a specific resource identifier."""
        if identifier not in self._results:
            raise KeyError(f"Resource '{identifier}' not found in discovery results.")
        return self._results[identifier]

    def enumerate_results(self) -> List[DiscoveryResult]:
        """Return a list of all current discovery results."""
        return list(self._results.values())
