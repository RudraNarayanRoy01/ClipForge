from typing import Protocol
from .dtos import (
    MediaMetadata,
    ClipExtractionRequest,
    AudioExtractionRequest,
    ThumbnailGenerationRequest,
    GenericMediaProcessingRequest,
    MediaProcessingResponse
)

class IMediaProcessor(Protocol):
    """
    Technology-agnostic interface for media processing operations.
    Implementations (e.g., FFmpeg) should raise exceptions derived from MediaProcessingError on failure.
    """
    
    def get_metadata(self, file_path: str) -> MediaMetadata:
        """Retrieves metadata for a given media file."""
        ...

    def extract_clip(self, request: ClipExtractionRequest) -> MediaProcessingResponse:
        """Extracts a video clip based on the requested parameters."""
        ...

    def extract_audio(self, request: AudioExtractionRequest) -> MediaProcessingResponse:
        """Extracts an audio track from the given media."""
        ...

    def generate_thumbnail(self, request: ThumbnailGenerationRequest) -> MediaProcessingResponse:
        """Generates a thumbnail image from the media at the specified timestamp."""
        ...

    def process_generic(self, request: GenericMediaProcessingRequest) -> MediaProcessingResponse:
        """
        Executes a generic or custom media processing operation.
        Useful for operations not covered by standard methods.
        """
        ...
