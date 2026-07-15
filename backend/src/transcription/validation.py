from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel

from .dtos import Transcript


class TranscriptValidationResult(BaseModel):
    """
    Model representing the outcome of transcript validation.
    """
    is_valid: bool
    errors: List[str]
    transcript: Optional[Transcript] = None

    class Config:
        frozen = True


class TranscriptValidationService:
    """
    Service responsible for structural transcript validation and metadata enrichment.
    Follows Clean Architecture by remaining independent of persistence and provider implementations.
    """

    def validate_and_enrich(self, transcript: Transcript, provider: str, model: str) -> TranscriptValidationResult:
        """
        Validates the transcript structure and enriches missing metadata.
        Performs validation in a single pass to optimize performance.
        
        Args:
            transcript: The input transcript domain model.
            provider: The name of the transcription provider (e.g., 'whisper').
            model: The name of the specific model used.
            
        Returns:
            TranscriptValidationResult: The validation result containing errors or the enriched transcript.
        """
        errors: List[str] = []

        if not transcript.full_text or not transcript.full_text.strip():
            errors.append("Transcript must contain text.")

        if not transcript.language:
            errors.append("Transcript language must be present.")

        last_segment_end = -1.0
        word_count = 0
        segment_count = len(transcript.segments)

        for i, segment in enumerate(transcript.segments):
            if not segment.text or not segment.text.strip():
                errors.append(f"Segment {i} text cannot be empty.")

            if segment.end_time <= segment.start_time:
                errors.append(f"Segment {i} duration must be positive.")

            # We use a small epsilon to avoid floating point precision issues for exact alignments
            if segment.start_time < last_segment_end - 1e-4:
                errors.append(f"Segment {i} overlaps with previous segment or is out of order.")

            last_segment_end = max(last_segment_end, segment.end_time)

            last_word_end = -1.0
            for j, word in enumerate(segment.words):
                word_count += 1
                
                if word.confidence is not None and not (0.0 <= word.confidence <= 1.0):
                    errors.append(f"Word {j} in segment {i} has invalid confidence: {word.confidence}")
                
                if word.start_time is not None and word.end_time is not None:
                    if word.start_time < last_word_end - 1e-4:
                        errors.append(f"Word {j} in segment {i} is out of order.")
                        
                    last_word_end = max(last_word_end, word.end_time)
                    
                    if word.start_time < segment.start_time - 1e-4 or word.end_time > segment.end_time + 1e-4:
                        errors.append(f"Word {j} in segment {i} timestamps are not contained within parent segment.")

        # Determine total duration based on the last segment's end time
        transcript_duration = last_segment_end if last_segment_end > 0 else 0.0
        if transcript_duration <= 0.0 and transcript.segments:
            errors.append("Transcript duration must be positive.")
        elif not transcript.segments:
            # If no segments exist but full_text does, we can't definitively check duration via segments.
            errors.append("Transcript must contain at least one segment to determine duration.")

        if errors:
            return TranscriptValidationResult(is_valid=False, errors=errors, transcript=None)

        # Metadata Enrichment
        # Ensure we do not modify the original immutable dictionary directly
        new_metadata = dict(transcript.metadata) if transcript.metadata else {}

        if "provider" not in new_metadata:
            new_metadata["provider"] = provider
        if "model" not in new_metadata:
            new_metadata["model"] = model
        if "language" not in new_metadata:
            new_metadata["language"] = transcript.language
        if "transcript_duration" not in new_metadata:
            new_metadata["transcript_duration"] = transcript_duration
        if "generation_timestamp" not in new_metadata:
            new_metadata["generation_timestamp"] = datetime.now(timezone.utc).isoformat()
        if "segment_count" not in new_metadata:
            new_metadata["segment_count"] = segment_count
        if "word_count" not in new_metadata:
            new_metadata["word_count"] = word_count

        # Support both Pydantic v1 and v2 for copying immutable models
        try:
            enriched_transcript = transcript.model_copy(update={"metadata": new_metadata})
        except AttributeError:
            enriched_transcript = transcript.copy(update={"metadata": new_metadata})

        return TranscriptValidationResult(is_valid=True, errors=[], transcript=enriched_transcript)
