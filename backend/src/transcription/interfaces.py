from abc import ABC, abstractmethod
from .dtos import TranscriptionRequest, Transcript


class ITranscriptionService(ABC):
    """
    High-level business service interface for transcription intelligence.
    Acts as the entry point for business logic requiring transcription.
    
    Business logic must depend on this interface, never on a concrete provider
    (e.g., Whisper, Deepgram), enforcing Clean Architecture principles.
    """
    
    @abstractmethod
    async def transcribe(self, request: TranscriptionRequest) -> Transcript:
        """
        Process media and return a unified transcript.
        
        Args:
            request: The transcription request detailing the media and configuration options.
            
        Returns:
            Transcript: The provider-agnostic transcription result.
            
        Raises:
            TranscriptionError: On general transcription failures.
            TranscriptionProcessingError: If the media fails to be transcribed.
        """
        pass
