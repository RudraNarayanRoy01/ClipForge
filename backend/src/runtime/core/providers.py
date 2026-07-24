from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Any
from datetime import datetime

class ProviderCategory(Enum):
    """
    Architectural categories for Runtime providers.
    
    Categories exist solely for organization. They must NEVER imply:
    - scheduling
    - execution priority
    - provider quality
    - benchmarking
    - hardware preference
    """
    LANGUAGE = "LANGUAGE"
    VISION = "VISION"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    REASONING = "REASONING"
    INFRASTRUCTURE = "INFRASTRUCTURE"


@dataclass(frozen=True)
class ProviderIdentity:
    """
    Represents a permanent architectural identity for a provider implementation.
    
    Provider identities should remain stable across Runtime versions.
    They identify implementations (e.g. openai.gpt, ollama.gemma3) - not runtime instances,
    execution state, or hardware.
    """
    identifier: str


@dataclass(frozen=True)
class ProviderDescriptor:
    """
    Immutable Runtime Provider Descriptor.
    
    Represents an architectural definition of a provider.
    
    Must avoid:
    - runtime state
    - benchmark results
    - performance metrics
    - execution statistics
    - hardware requirements
    
    After registration, all fields (identifier, capabilities, resources, category, etc.)
    remain completely immutable.
    """
    identity: ProviderIdentity
    display_name: str
    description: str
    supported_capability_ids: list[str] = field(default_factory=list)
    supported_resource_ids: list[str] = field(default_factory=list)
    category: ProviderCategory = ProviderCategory.LANGUAGE
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: Optional[str] = None


@dataclass(frozen=True)
class ProviderRegistration:
    """
    Represents the architectural registration of a provider.
    
    This separates provider definitions from future runtime selection.
    
    It should NOT contain:
    - execution state
    - scheduling information
    - benchmark scores
    - health status
    - runtime metrics
    - provider priority
    
    Future Runtime systems should build on top of this rather than modifying it.
    """
    descriptor: ProviderDescriptor
    registered_at: datetime


class RuntimeProviderRegistry:
    """
    The canonical catalog of provider implementations for the Runtime.
    
    Responsibilities:
    - Own ProviderDescriptors
    - Register/unregister providers
    - Enumerate/lookup providers
    - Validate duplicate registrations
    
    MUST NOT:
    - Instantiate, resolve, select, or execute providers
    - Benchmark, schedule, monitor health, or optimize
    
    This registry should remain execution-independent.
    """
    def __init__(self) -> None:
        self._registrations: Dict[ProviderIdentity, ProviderRegistration] = {}

    def register_provider(self, descriptor: ProviderDescriptor) -> ProviderRegistration:
        """
        Register a new provider.
        Raises ValueError if a provider with the same identity is already registered.
        """
        if descriptor.identity in self._registrations:
            raise ValueError(f"Provider '{descriptor.identity.identifier}' is already registered.")
        
        registration = ProviderRegistration(
            descriptor=descriptor,
            registered_at=datetime.utcnow()
        )
        self._registrations[descriptor.identity] = registration
        return registration

    def unregister_provider(self, identity: ProviderIdentity) -> None:
        """
        Unregister a provider by its identity.
        Raises KeyError if not found.
        """
        if identity not in self._registrations:
            raise KeyError(f"Provider '{identity.identifier}' is not registered.")
        del self._registrations[identity]

    def get_provider(self, identity: ProviderIdentity) -> ProviderRegistration:
        """
        Lookup a provider registration by its identity.
        Raises KeyError if not found.
        """
        if identity not in self._registrations:
            raise KeyError(f"Provider '{identity.identifier}' is not registered.")
        return self._registrations[identity]

    def enumerate_providers(self) -> list[ProviderRegistration]:
        """
        Return a list of all current provider registrations.
        """
        return list(self._registrations.values())
