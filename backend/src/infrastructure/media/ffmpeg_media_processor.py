import os
import time
import json
import logging
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
    MediaProcessingError
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
        
        command = [
            self.settings.ffprobe_executable_path,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            file_path
        ]
        
        result = self.executor.execute_command(command)
        
        try:
            data = json.loads(result.stdout)
            
            # Find first video stream
            video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
            # Check for audio stream
            audio_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
            
            format_info = data.get("format", {})
            
            duration_seconds = float(format_info.get("duration", 0.0))
            
            width = 0
            height = 0
            fps = 0.0
            
            if video_stream:
                width = int(video_stream.get("width", 0))
                height = int(video_stream.get("height", 0))
                # fps can be a fraction string like "30000/1001" or "30/1"
                r_frame_rate = video_stream.get("r_frame_rate", "0/1")
                try:
                    num, den = map(int, r_frame_rate.split('/'))
                    if den != 0:
                        fps = num / den
                except (ValueError, ZeroDivisionError):
                    fps = 0.0
            
            has_audio = audio_stream is not None
            format_name = format_info.get("format_name", "")
            
            bitrate_str = format_info.get("bitrate")
            bitrate = int(bitrate_str) if bitrate_str is not None else None
            
            return MediaMetadata(
                duration_seconds=duration_seconds,
                width=width,
                height=height,
                fps=fps,
                has_audio=has_audio,
                format_name=format_name,
                bitrate=bitrate,
                extra_info=data
            )
        except Exception as e:
            raise MediaProcessingError(f"Failed to parse metadata from ffprobe output: {str(e)}") from e

    def extract_clip(self, request: ClipExtractionRequest) -> MediaProcessingResponse:
        """Extracts a video clip based on the requested parameters."""
        self._validate_input_path(request.source_path)
        self._prepare_output_path(request.output_path)
        
        if request.start_time < 0:
            raise MediaProcessingError(f"Invalid start time: {request.start_time}. Must be non-negative.")
            
        duration = request.end_time - request.start_time
        if duration <= 0:
            raise MediaProcessingError(f"Invalid clip boundaries. Requested clip length must be positive (start: {request.start_time}, end: {request.end_time}).")
            
        command = [
            self.settings.ffmpeg_executable_path,
            "-y",  # Overwrite output files
            "-ss", str(request.start_time),  # Fast seek before input
            "-i", request.source_path,
            "-t", str(duration),
            "-c", "copy",  # Direct stream copy for fast extraction without re-encoding
            request.output_path
        ]
        
        start_time_exec = time.time()
        
        # SubprocessExecutor handles timeouts, exception translation, and shell=False enforcement.
        self.executor.execute_command(command)
        
        execution_time = time.time() - start_time_exec
        
        return MediaProcessingResponse(
            success=True,
            output_path=request.output_path,
            execution_time_seconds=execution_time
        )

    def extract_audio(self, request: AudioExtractionRequest) -> MediaProcessingResponse:
        """Extracts an audio track from the given media."""
        self._validate_input_path(request.source_path)
        self._prepare_output_path(request.output_path)
        
        if not request.output_path:
            raise MediaProcessingError("Output path cannot be empty.")
            
        if request.target_sample_rate <= 0:
            raise MediaProcessingError(f"Invalid target sample rate: {request.target_sample_rate}. Must be positive.")
            
        if request.target_channels <= 0:
            raise MediaProcessingError(f"Invalid target channels: {request.target_channels}. Must be positive.")
            
        command = [
            self.settings.ffmpeg_executable_path,
            "-y",  # Overwrite output files
            "-i", request.source_path,
            "-vn",  # Disable video processing
        ]
        
        # Applying specific format conversion as requested by the DTO.
        command.extend([
            "-ar", str(request.target_sample_rate),
            "-ac", str(request.target_channels),
            request.output_path
        ])
        
        start_time_exec = time.time()
        
        # SubprocessExecutor handles timeouts, exception translation, and shell=False enforcement.
        self.executor.execute_command(command)
        
        execution_time = time.time() - start_time_exec
        
        return MediaProcessingResponse(
            success=True,
            output_path=request.output_path,
            execution_time_seconds=execution_time
        )

    def generate_thumbnail(self, request: ThumbnailGenerationRequest) -> MediaProcessingResponse:
        """Generates a thumbnail image from the media at the specified timestamp."""
        self._validate_input_path(request.source_path)
        self._prepare_output_path(request.output_path)
        
        if request.timestamp < 0:
            raise MediaProcessingError(f"Invalid timestamp: {request.timestamp}. Must be non-negative.")
            
        command = [
            self.settings.ffmpeg_executable_path,
            "-y",  # Overwrite output files
            "-ss", str(request.timestamp),  # Seek to timestamp
            "-i", request.source_path,
            "-vframes", "1",  # Output exactly one frame
        ]
        
        # Add scaling if dimensions are provided
        if request.target_width is not None and request.target_height is not None:
            command.extend(["-vf", f"scale={request.target_width}:{request.target_height}"])
        elif request.target_width is not None:
            command.extend(["-vf", f"scale={request.target_width}:-1"])
        elif request.target_height is not None:
            command.extend(["-vf", f"scale=-1:{request.target_height}"])
            
        command.append(request.output_path)
        
        start_time_exec = time.time()
        
        # SubprocessExecutor handles timeouts, exception translation, and shell=False enforcement.
        self.executor.execute_command(command)
        
        execution_time = time.time() - start_time_exec
        
        return MediaProcessingResponse(
            success=True,
            output_path=request.output_path,
            execution_time_seconds=execution_time
        )

    def process_generic(self, request: GenericMediaProcessingRequest) -> MediaProcessingResponse:
        """Executes a generic or custom media processing operation."""
        self._validate_input_path(request.source_path)
        self._prepare_output_path(request.output_path)
        raise NotImplementedError("Generic media processing will be implemented in a future batch.")
