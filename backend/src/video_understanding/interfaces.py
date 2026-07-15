from abc import ABC, abstractmethod
from .dtos import VideoAnalysisRequest, VideoUnderstandingResult


class IVideoUnderstandingService(ABC):
    """
    High-level business service interface for AI Video Understanding.
    Acts as the entry point for intelligent analysis of video content.
    
    Business logic must depend on this interface, never on a concrete AI provider
    (e.g., OpenAI, Anthropic, Gemini, Ollama), enforcing Clean Architecture principles.
    """
    
    @abstractmethod
    async def analyze_video(self, request: VideoAnalysisRequest) -> VideoUnderstandingResult:
        """
        Analyze the provided video transcript and extract rich understanding metadata
        such as topics, entities, hooks, highlights, and sentiment.
        
        Args:
            request: The request containing the video transcript and analysis configuration.
            
        Returns:
            VideoUnderstandingResult: The provider-agnostic structured understanding result.
            
        Raises:
            VideoUnderstandingError: On general understanding failures.
            ProviderConnectionError: If the underlying AI provider is unreachable.
            ContextLengthExceededError: If the input exceeds the provider's token limit.
        """
        pass
