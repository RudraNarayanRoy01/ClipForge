class VideoUnderstandingError(Exception):
    """Base exception for all video understanding errors."""
    pass


class ProviderConnectionError(VideoUnderstandingError):
    """Raised when the AI provider cannot be reached (network/connectivity)."""
    pass


class ProviderTimeoutError(VideoUnderstandingError):
    """Raised when the AI provider request times out."""
    pass


class ProviderConfigurationError(VideoUnderstandingError):
    """Raised when the AI provider is misconfigured."""
    pass


class VideoUnderstandingProcessingError(VideoUnderstandingError):
    """Raised when the AI engine fails to process the video context."""
    pass


class VideoUnderstandingValidationError(VideoUnderstandingError):
    """Raised when an understanding result fails structural or business validation rules."""
    pass


class ContextLengthExceededError(VideoUnderstandingError):
    """Raised when the provided transcript or video context exceeds the AI model's token limit."""
    pass


class ContentModerationError(VideoUnderstandingError):
    """Raised when the AI provider rejects the input due to content moderation policies."""
    pass
