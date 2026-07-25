from typing import Dict, List
from ..domain.provider_registry_model import ProviderInfo, ProviderRegistryResult

class ProviderRegistry:
    """
    The canonical metadata registry for Provider Identity in the AI Clipping Platform.
    
    Responsibilities:
    - Register provider identities
    - Unregister provider identities
    - Enumerate/lookup provider identities
    
    Ownership:
    - Owns ProviderInfo
    - Owns ProviderStatus
    - Owns ProviderType
    - Produces ProviderRegistryResult
    
    MUST NOT:
    - Become a Provider Factory, Builder, Loader, Resolver, or Selector.
    - Manage Provider Lifecycle, Health, Capability, Authentication, or Networking.
    - Execute providers or route requests.
    
    It only answers "What providers exist?". It never answers "Which provider should I use?".
    """
    def __init__(self) -> None:
        self._providers: Dict[str, ProviderInfo] = {}

    def register(self, provider_info: ProviderInfo) -> ProviderRegistryResult:
        """
        Register a new provider identity.
        Raises ValueError if a provider with the same identity is already registered.
        """
        if provider_info.provider_id in self._providers:
            raise ValueError(f"Provider '{provider_info.provider_id}' is already registered.")
        
        self._providers[provider_info.provider_id] = provider_info
        
        return ProviderRegistryResult(
            registered_providers=[provider_info],
            operation_summary=f"Successfully registered provider {provider_info.provider_id}.",
            registration_result=True
        )

    def unregister(self, provider_id: str) -> ProviderRegistryResult:
        """
        Unregister a provider by its identity.
        Raises KeyError if not found.
        """
        if provider_id not in self._providers:
            raise KeyError(f"Provider '{provider_id}' is not registered.")
        
        provider_info = self._providers.pop(provider_id)
        
        return ProviderRegistryResult(
            registered_providers=[provider_info],
            operation_summary=f"Successfully unregistered provider {provider_id}.",
            registration_result=True
        )

    def get_provider(self, provider_id: str) -> ProviderInfo:
        """
        Lookup a provider registration by its identity.
        Raises KeyError if not found.
        """
        if provider_id not in self._providers:
            raise KeyError(f"Provider '{provider_id}' is not registered.")
        return self._providers[provider_id]

    def list_providers(self) -> List[ProviderInfo]:
        """
        Return a list of all current provider identities.
        """
        return list(self._providers.values())

    def provider_exists(self, provider_id: str) -> bool:
        """
        Check if a provider identity is registered.
        """
        return provider_id in self._providers
