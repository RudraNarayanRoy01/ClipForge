from typing import Dict, List
from ..domain.provider_capability_model import ProviderCapability, ProviderCapabilityResult

class ProviderCapabilityRegistry:
    """
    The canonical metadata registry for Provider Capability in the AI Clipping Platform.
    
    Responsibilities:
    - register_capability()
    - update_capability()
    - remove_capability()
    - get_capability()
    - list_capabilities()
    - capability_exists()
    
    Ownership:
    - Owns ProviderCapability
    - Owns CapabilityLimits
    - Owns CapabilityType
    - Produces ProviderCapabilityResult
    
    MUST NOT:
    - Execute providers
    - Evaluate providers
    - Select providers
    - Compare or rank providers
    - Route requests
    - Manage lifecycle, health, or failover
    - Perform reasoning or scheduling
    
    It only answers "What capabilities does this provider support?". 
    It never answers "Which provider should I use?".
    """
    def __init__(self) -> None:
        self._capabilities: Dict[str, ProviderCapability] = {}

    def register_capability(self, capability: ProviderCapability) -> ProviderCapabilityResult:
        """
        Register a new provider capability.
        Raises ValueError if a capability for the provider_id is already registered.
        """
        if capability.provider_id in self._capabilities:
            raise ValueError(f"Capability for provider '{capability.provider_id}' is already registered.")
        
        self._capabilities[capability.provider_id] = capability
        
        return ProviderCapabilityResult(
            provider_capability=capability,
            operation_summary=f"Successfully registered capabilities for provider {capability.provider_id}.",
            validation_result=True
        )

    def update_capability(self, capability: ProviderCapability) -> ProviderCapabilityResult:
        """
        Update an existing provider capability.
        Raises KeyError if the capability is not registered.
        """
        if capability.provider_id not in self._capabilities:
            raise KeyError(f"Capability for provider '{capability.provider_id}' is not registered.")
        
        self._capabilities[capability.provider_id] = capability
        
        return ProviderCapabilityResult(
            provider_capability=capability,
            operation_summary=f"Successfully updated capabilities for provider {capability.provider_id}.",
            validation_result=True
        )

    def remove_capability(self, provider_id: str) -> ProviderCapabilityResult:
        """
        Remove a provider's capability registration.
        Raises KeyError if not found.
        """
        if provider_id not in self._capabilities:
            raise KeyError(f"Capability for provider '{provider_id}' is not registered.")
        
        capability = self._capabilities.pop(provider_id)
        
        return ProviderCapabilityResult(
            provider_capability=capability,
            operation_summary=f"Successfully removed capabilities for provider {provider_id}.",
            validation_result=True
        )

    def get_capability(self, provider_id: str) -> ProviderCapability:
        """
        Retrieve a provider's capabilities by provider_id.
        Raises KeyError if not found.
        """
        if provider_id not in self._capabilities:
            raise KeyError(f"Capability for provider '{provider_id}' is not registered.")
        return self._capabilities[provider_id]

    def list_capabilities(self) -> List[ProviderCapability]:
        """
        Return a list of all registered provider capabilities.
        """
        return list(self._capabilities.values())

    def capability_exists(self, provider_id: str) -> bool:
        """
        Check if a capability for the provider identity is registered.
        """
        return provider_id in self._capabilities
