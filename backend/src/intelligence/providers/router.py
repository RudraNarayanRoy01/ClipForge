from typing import List, Type, Any
from .local.gemma4 import Gemma4LocalProvider
from .capabilities import IReasoning

class CapabilityRouter:
    def __init__(self):
        # In a real scenario, this would be injected and populated by plugin loader
        self._providers = [
            Gemma4LocalProvider()
        ]

    def resolve(self, requires: List[Type]) -> Any:
        # Find first provider that implements all required protocols
        for provider in self._providers:
            # Simplistic check for MVP: check if provider is subclass of required protocols
            if all(isinstance(provider, req) for req in requires):
                return provider
        
        raise ValueError(f"No provider found satisfying capabilities: {requires}")

# Example usage
router = CapabilityRouter()
