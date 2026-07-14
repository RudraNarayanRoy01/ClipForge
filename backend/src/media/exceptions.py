class MediaProcessingError(Exception):
    """Base exception for all media processing failures."""
    pass

class MediaInputNotFoundError(MediaProcessingError):
    """Raised when the input media file does not exist."""
    pass

class MediaOutputWriteError(MediaProcessingError):
    """Raised when the output path is invalid or cannot be written to."""
    pass

class InvalidMediaFormatError(MediaProcessingError):
    """Raised when the media format is unsupported or corrupt."""
    pass

class MediaProcessingTimeoutError(MediaProcessingError):
    """Raised when a media processing operation exceeds its time limit."""
    pass

class SubprocessExecutionError(MediaProcessingError):
    """Raised when the underlying processor (e.g., FFmpeg) fails."""
    def __init__(self, message: str, exit_code: int = -1, stderr: str = ""):
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr
