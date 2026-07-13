from src.config.ai_settings import AISettings
from src.intelligence.providers.registry import ProviderRegistry
from src.intelligence.providers.capabilities import IAIProvider
from src.intelligence.exceptions.ai import AIConfigurationError

class ProviderFactory:
    """
    Factory for instantiating the correct AI provider based on configuration.
    Acts as the single provider resolution mechanism.
    """
    def __init__(self, settings: AISettings):
        self._settings = settings

    def create_provider(self) -> IAIProvider:
        """
        Resolves the provider builder from the registry and instantiates it.
        Raises AIConfigurationError if the requested provider is unknown.
        """
        provider_name = self._settings.ai_provider
        provider_builder = ProviderRegistry.get_provider_builder(provider_name)

        if not provider_builder:
            raise AIConfigurationError(
                f"Unknown or unregistered AI provider: '{provider_name}'. "
                f"Please ensure it is registered in the ProviderRegistry."
            )

        # Call the builder with settings to instantiate the provider
        return provider_builder(self._settings)
