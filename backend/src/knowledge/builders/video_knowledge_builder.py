from datetime import datetime, timezone
from typing import Optional

from src.media.dtos import MediaMetadata
from src.transcription.dtos import Transcript
from src.video_understanding.dtos import VideoUnderstandingResult
from src.knowledge.dtos import VideoKnowledge, KnowledgeStatus, KnowledgeMetadata


class VideoKnowledgeBuilder:
    """
    Factory responsible for assembling validated domain models into a canonical VideoKnowledge snapshot.
    This is the ONLY component allowed to determine KnowledgeStatus.
    """

    def __init__(self, provider_identifier: str = "clipforge_internal", source_version: str = "1.0") -> None:
        """
        Initializes the builder with baseline metadata.
        """
        self._provider_identifier = provider_identifier
        self._source_version = source_version
        self._schema_version = "1.0"
        self._knowledge_version = "1.0"
        
        # Domain model state
        self._media_metadata: Optional[MediaMetadata] = None
        self._transcript: Optional[Transcript] = None
        self._understanding: Optional[VideoUnderstandingResult] = None

    def with_media_metadata(self, media_metadata: MediaMetadata) -> 'VideoKnowledgeBuilder':
        """
        Attaches media metadata to the knowledge snapshot.
        Only accepts the validated MediaMetadata domain model.
        """
        if not isinstance(media_metadata, MediaMetadata):
            raise TypeError("media_metadata must be a validated MediaMetadata domain model")
        self._media_metadata = media_metadata
        return self

    def with_transcript(self, transcript: Transcript) -> 'VideoKnowledgeBuilder':
        """
        Attaches a transcript to the knowledge snapshot.
        Only accepts the validated Transcript domain model.
        """
        if not isinstance(transcript, Transcript):
            raise TypeError("transcript must be a validated Transcript domain model")
        self._transcript = transcript
        return self

    def with_understanding(self, understanding: VideoUnderstandingResult) -> 'VideoKnowledgeBuilder':
        """
        Attaches video understanding results to the knowledge snapshot.
        Only accepts the validated VideoUnderstandingResult domain model.
        """
        if not isinstance(understanding, VideoUnderstandingResult):
            raise TypeError("understanding must be a validated VideoUnderstandingResult domain model")
        self._understanding = understanding
        return self

    def build(self) -> VideoKnowledge:
        """
        Validates aggregate consistency, determines KnowledgeStatus, and builds 
        the immutable VideoKnowledge snapshot.
        
        Always returns a canonical VideoKnowledge instance. Does not expose
        partially assembled intermediate objects.
        """
        status = self._determine_status()
        
        metadata = KnowledgeMetadata(
            schema_version=self._schema_version,
            knowledge_version=self._knowledge_version,
            processing_timestamp=datetime.now(timezone.utc),
            provider_identifier=self._provider_identifier,
            source_version=self._source_version
        )
        
        return VideoKnowledge(
            status=status,
            metadata=metadata,
            media_metadata=self._media_metadata,
            transcript=self._transcript,
            understanding=self._understanding
        )
        
    def _determine_status(self) -> KnowledgeStatus:
        """
        Deterministic business rules for knowledge completeness status.
        This is the single source of truth for KnowledgeStatus determination.
        """
        if self._is_invalid():
            return KnowledgeStatus.INVALID
            
        if not self._transcript:
            return KnowledgeStatus.PENDING
            
        if self._media_metadata and self._transcript and self._understanding:
            return KnowledgeStatus.COMPLETE
            
        return KnowledgeStatus.PARTIAL
        
    def _is_invalid(self) -> bool:
        """
        Validates aggregate consistency to detect structural anomalies.
        Does not repair data; simply marks as INVALID if inconsistencies are found.
        """
        # 1. Structural Completeness & Sanity Checks
        if self._media_metadata and self._media_metadata.duration_seconds <= 0:
            return True
            
        # 2. Transcript Consistency
        if self._transcript:
            if not self._transcript.full_text and self._transcript.segments:
                return True
                
            for segment in self._transcript.segments:
                if segment.start_time < 0 or segment.end_time < segment.start_time:
                    return True
                    
        # 3. Cross-Domain Timestamp Consistency
        # Allow a reasonable tolerance for processing artifacts (e.g. 5 seconds)
        TOLERANCE = 5.0 
        
        if self._media_metadata and self._transcript and self._transcript.segments:
            last_segment = self._transcript.segments[-1]
            if last_segment.end_time > self._media_metadata.duration_seconds + TOLERANCE:
                return True
                
        if self._media_metadata and self._understanding:
            for topic in self._understanding.topics:
                if topic.end_time > self._media_metadata.duration_seconds + TOLERANCE:
                    return True
            for highlight in self._understanding.highlights:
                if highlight.end_time > self._media_metadata.duration_seconds + TOLERANCE:
                    return True
                    
        return False
