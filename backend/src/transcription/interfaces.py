from abc import ABC, abstractmethod
import uuid
from .dtos import TranscriptionRequest, Transcript


class ITranscriptRepository(ABC):
    """
    Repository interface for persisting Transcripts and their segments/words.
    Follows Clean Architecture by defining the persistence port in the application layer.
    """
    
    @abstractmethod
    async def save_transcript(self, video_asset_id: uuid.UUID, transcript: Transcript) -> None:
        """
        Persists a complete transcript associated with a video asset.
        Overwrites any existing transcript for this video asset.
        """
        pass
        
    @abstractmethod
    async def get_transcript(self, video_asset_id: uuid.UUID) -> Transcript:
        """
        Retrieves a transcript for a given video asset.
        Raises a ValueError if the transcript is not found.
        """
        pass


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
