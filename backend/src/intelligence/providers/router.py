from typing import List, Type, Any, Optional
from src.intelligence.providers.local.gemma4 import Gemma4LocalProvider
from src.intelligence.providers.factory import ProviderFactory
from src.intelligence.providers.capabilities import IAIProvider

class CapabilityRouter:
    def __init__(self, factory: Optional[ProviderFactory] = None):
        """
        Legacy capability router. 
        Adapted to optionally accept modern ProviderFactory via DI.
        """
        self._providers: List[IAIProvider] = []
        
        # If modern factory is injected, resolve the modern provider
        if factory:
            self._providers.append(factory.create_provider())
            
        # Always include the legacy mock provider for backward compatibility
        self._providers.append(Gemma4LocalProvider())

    def resolve(self, requires: List[Type]) -> Any:
        # Find first provider that implements all required protocols
        for provider in self._providers:
            # Simplistic check for MVP: check if provider is subclass of required protocols
            if all(isinstance(provider, req) for req in requires):
                return provider
        
        raise ValueError(f"No provider found satisfying capabilities: {requires}")

# Example usage (Legacy)
router = CapabilityRouter()
