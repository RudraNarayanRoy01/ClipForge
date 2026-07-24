from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List
from datetime import datetime


class HardwareCategory(Enum):
    """
    Architectural categories for Runtime hardware resources.
    
    Categories exist solely for organization. They must NEVER imply:
    - scheduling
    - execution priority
    - performance capability
    - benchmarking
    """
    CPU = "CPU"
    GPU = "GPU"
    MEMORY = "MEMORY"
    NPU = "NPU"
    TPU = "TPU"
    ACCELERATOR = "ACCELERATOR"
    STORAGE = "STORAGE"


@dataclass(frozen=True)
class HardwareIdentity:
    """
    Represents a permanent architectural identity for a hardware device.
    
    Hardware identities should remain stable across Runtime versions.
    They identify devices (e.g. 'cpu.main', 'gpu.cuda0') - not runtime utilization,
    execution state, provider assignment, or scheduling.
    """
    identifier: str


@dataclass(frozen=True)
class HardwareDescriptor:
    """
    Immutable Runtime Hardware Descriptor.
    
    Represents an architectural definition of hardware properties.
    
    Must avoid storing runtime state such as:
    - utilization
    - available memory
    - occupied VRAM
    - active processes
    - temperatures
    - clock speeds
    - runtime metrics
    
    After registration, all fields remain completely immutable.
    """
    identity: HardwareIdentity
    display_name: str
    description: str
    category: HardwareCategory
    vendor: str
    architecture: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HardwareRegistration:
    """
    Represents the architectural registration of a discovered hardware device.
    
    This separates hardware definitions from future runtime scheduling.
    
    It should NOT contain:
    - utilization
    - scheduling state
    - benchmark scores
    - health information
    - runtime metrics
    - allocation state
    
    Future Runtime systems should build on top of this rather than modifying it.
    """
    descriptor: HardwareDescriptor
    registered_at: datetime


class RuntimeHardwareDiscovery:
    """
    The canonical catalog of available hardware resources for the Runtime.
    
    Responsibilities:
    - Discover hardware resources
    - Register hardware resources
    - Unregister hardware resources
    - Enumerate hardware
    - Lookup hardware
    - Validate duplicate registrations
    
    MUST NOT:
    - Allocate or reserve hardware
    - Benchmark or monitor hardware
    - Schedule hardware or execute workloads
    - Optimize hardware usage or expose runtime utilization
    
    This registry should remain execution-independent and architecture-only.
    """
    def __init__(self) -> None:
        self._registrations: Dict[HardwareIdentity, HardwareRegistration] = {}

    def register_hardware(self, descriptor: HardwareDescriptor) -> HardwareRegistration:
        """
        Register a newly discovered hardware device.
        Raises ValueError if a device with the same identity is already registered.
        """
        if descriptor.identity in self._registrations:
            raise ValueError(f"Hardware '{descriptor.identity.identifier}' is already registered.")
        
        registration = HardwareRegistration(
            descriptor=descriptor,
            registered_at=datetime.utcnow()
        )
        self._registrations[descriptor.identity] = registration
        return registration

    def unregister_hardware(self, identity: HardwareIdentity) -> None:
        """
        Unregister a hardware device by its identity.
        Raises KeyError if not found.
        """
        if identity not in self._registrations:
            raise KeyError(f"Hardware '{identity.identifier}' is not registered.")
        del self._registrations[identity]

    def get_hardware(self, identity: HardwareIdentity) -> HardwareRegistration:
        """
        Lookup a hardware registration by its identity.
        Raises KeyError if not found.
        """
        if identity not in self._registrations:
            raise KeyError(f"Hardware '{identity.identifier}' is not registered.")
        return self._registrations[identity]

    def enumerate_hardware(self) -> List[HardwareRegistration]:
        """
        Return a list of all current hardware registrations.
        """
        return list(self._registrations.values())
