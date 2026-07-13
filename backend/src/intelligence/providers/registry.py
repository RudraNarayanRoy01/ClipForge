from typing import Dict, Callable
from src.intelligence.providers.capabilities import IAIProvider
from src.config.ai_settings import AISettings

ProviderBuilder = Callable[[AISettings], IAIProvider]

class ProviderRegistry:
    """
    Lightweight registry mapping provider names to provider builders.
    Centralizes provider registration and simplifies future additions.
    """
    _providers: Dict[str, ProviderBuilder] = {}

    @classmethod
    def register(cls, name: str, builder: ProviderBuilder) -> None:
        """Register a new provider builder function."""
        cls._providers[name] = builder

    @classmethod
    def get_provider_builder(cls, name: str) -> ProviderBuilder:
        """Retrieve a provider builder by name."""
        return cls._providers.get(name)

    @classmethod
    def clear(cls) -> None:
        """Clear the registry (useful for testing)."""
        cls._providers.clear()
