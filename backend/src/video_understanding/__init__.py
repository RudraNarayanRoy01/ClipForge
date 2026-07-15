"""
AI Video Understanding module.
Provides abstract interfaces and DTOs for performing AI-driven video analysis.
"""

from .dtos import (
    Topic,
    Entity,
    Hook,
    Highlight,
    Sentiment,
    VideoUnderstandingResult,
    VideoAnalysisRequest,
)
from .exceptions import (
    VideoUnderstandingError,
    ProviderConnectionError,
    ProviderTimeoutError,
    ProviderConfigurationError,
    VideoUnderstandingProcessingError,
    VideoUnderstandingValidationError,
    ContextLengthExceededError,
    ContentModerationError,
)
from .interfaces import IVideoUnderstandingService

__all__ = [
    "Topic",
    "Entity",
    "Hook",
    "Highlight",
    "Sentiment",
    "VideoUnderstandingResult",
    "VideoAnalysisRequest",
    "VideoUnderstandingError",
    "ProviderConnectionError",
    "ProviderTimeoutError",
    "ProviderConfigurationError",
    "VideoUnderstandingProcessingError",
    "VideoUnderstandingValidationError",
    "ContextLengthExceededError",
    "ContentModerationError",
    "IVideoUnderstandingService",
]
