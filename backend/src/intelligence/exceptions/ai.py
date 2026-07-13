class AIProviderError(Exception):
    """Base class for all AI provider exceptions."""
    pass

class AIConnectionError(AIProviderError):
    """Raised when the provider cannot be reached (network/connectivity)."""
    pass

class AITimeoutError(AIProviderError):
    """Raised when the provider request times out."""
    pass

class AIConfigurationError(AIProviderError):
    """Raised when the provider is misconfigured."""
    pass

class AIResponseValidationError(AIProviderError):
    """Raised when the provider returns an invalid schema or response format."""
    pass

class ModelNotAvailableError(AIProviderError):
    """Raised when the requested model is not found or not available."""
    pass
