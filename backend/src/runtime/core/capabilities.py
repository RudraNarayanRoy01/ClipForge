from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


class CapabilityCategory(Enum):
    """
    Architectural classifications for capabilities.
    
    These categories are purely organizational and do NOT imply
    provider selection, hardware requirements, or execution priority.
    """
    VISION = auto()
    AUDIO = auto()
    LANGUAGE = auto()
    VIDEO = auto()
    REASONING = auto()
    UTILITY = auto()


@dataclass(frozen=True)
class CapabilityDescriptor:
    """
    An immutable definition of a Runtime Capability.
    
    This descriptor represents a permanent architectural identity
    (e.g., 'vision.analysis', 'audio.transcription') describing WHAT 
    the Runtime understands, completely decoupled from HOW it executes.
    
    It intentionally avoids provider-specific or execution-state fields.
    """
    identifier: str
    display_name: str
    description: str
    category: CapabilityCategory
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: Optional[str] = None


class RuntimeCapabilityRegistry:
    """
    The canonical architectural catalog of Runtime capabilities.
    
    This registry is explicitly owned by the RuntimeContext. It is strictly 
    responsible for registering, looking up, and enumerating capability descriptors.
    
    It intentionally does NOT instantiate, discover, or execute providers.
    """
    
    def __init__(self) -> None:
        self._descriptors: Dict[str, CapabilityDescriptor] = {}

    def register_descriptor(self, descriptor: CapabilityDescriptor) -> None:
        """
        Register a new immutable capability descriptor.
        
        Raises a ValueError if a descriptor with the same identifier already exists.
        """
        if descriptor.identifier in self._descriptors:
            raise ValueError(f"Capability descriptor '{descriptor.identifier}' is already registered.")
        
        self._descriptors[descriptor.identifier] = descriptor

    def get_descriptor(self, identifier: str) -> CapabilityDescriptor:
        """
        Retrieve a capability descriptor by its permanent identifier.
        
        Raises a KeyError if the identifier is not found.
        """
        if identifier not in self._descriptors:
            raise KeyError(f"Capability descriptor '{identifier}' not found.")
        
        return self._descriptors[identifier]

    def enumerate_descriptors(self) -> List[CapabilityDescriptor]:
        """
        Return a list of all registered capability descriptors.
        """
        return list(self._descriptors.values())
