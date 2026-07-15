from abc import ABC, abstractmethod
import uuid
from typing import List, Optional
from .dtos import TranscriptionRequest, Transcript, TranscriptSearchResult

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

    @abstractmethod
    async def search_transcripts(self, query: str, video_asset_id: Optional[uuid.UUID] = None, limit: int = 50) -> List[TranscriptSearchResult]:
        """
        Searches transcripts for segments matching the keyword query.
        Results are ordered logically and executed efficiently at the database level.
        
        Raises a ValueError for invalid or excessively long queries.
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
