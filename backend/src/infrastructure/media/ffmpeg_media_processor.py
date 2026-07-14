import os
import logging
from typing import List, Any
from src.media.interfaces import IMediaProcessor
from src.media.dtos import (
    MediaMetadata,
    ClipExtractionRequest,
    AudioExtractionRequest,
    ThumbnailGenerationRequest,
    GenericMediaProcessingRequest,
    MediaProcessingResponse
)
from src.media.exceptions import (
    MediaInputNotFoundError,
    MediaOutputWriteError,
    MediaProcessingError,
    SubprocessExecutionError,
    MediaProcessingTimeoutError
)
from src.config.media_settings import MediaSettings
from src.infrastructure.media.subprocess_utility import SubprocessExecutor

logger = logging.getLogger(__name__)

class FFmpegMediaProcessor(IMediaProcessor):
    """
    Concrete implementation of IMediaProcessor using FFmpeg.
    Ensures safe execution of subprocesses and enforces separation of 
    concerns by keeping FFmpeg details within the infrastructure layer.
    """

    def __init__(self, settings: MediaSettings, executor: SubprocessExecutor):
        self.settings = settings
        self.executor = executor

    def _validate_input_path(self, file_path: str) -> None:
        """Validates that the input media file exists."""
        if not os.path.isfile(file_path):
            raise MediaInputNotFoundError(f"Input file not found: {file_path}")

    def _prepare_output_path(self, output_path: str) -> None:
        """Ensures the directory for the output file exists."""
        directory = os.path.dirname(output_path)
        if directory:
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                raise MediaOutputWriteError(f"Cannot create output directory {directory}: {str(e)}") from e

    def get_metadata(self, file_path: str) -> MediaMetadata:
        """Retrieves metadata for a given media file."""
        self._validate_input_path(file_path)
        raise NotImplementedError("Metadata extraction will be implemented in a future batch.")

    def extract_clip(self, request: ClipExtractionRequest) -> MediaProcessingResponse:
        """Extracts a video clip based on the requested parameters."""
        self._validate_input_path(request.source_path)
        self._prepare_output_path(request.output_path)
        raise NotImplementedError("Clip extraction will be implemented in a future batch.")

    def extract_audio(self, request: AudioExtractionRequest) -> MediaProcessingResponse:
        """Extracts an audio track from the given media."""
        self._validate_input_path(request.source_path)
        self._prepare_output_path(request.output_path)
        raise NotImplementedError("Audio extraction will be implemented in a future batch.")

    def generate_thumbnail(self, request: ThumbnailGenerationRequest) -> MediaProcessingResponse:
        """Generates a thumbnail image from the media at the specified timestamp."""
        self._validate_input_path(request.source_path)
        self._prepare_output_path(request.output_path)
        raise NotImplementedError("Thumbnail generation will be implemented in a future batch.")

    def process_generic(self, request: GenericMediaProcessingRequest) -> MediaProcessingResponse:
        """Executes a generic or custom media processing operation."""
        self._validate_input_path(request.source_path)
        self._prepare_output_path(request.output_path)
        raise NotImplementedError("Generic media processing will be implemented in a future batch.")
