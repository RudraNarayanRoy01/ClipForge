class TranscriptionError(Exception):
    """Base class for all transcription exceptions."""
    pass

class TranscriptionConnectionError(TranscriptionError):
    """Raised when the transcription provider cannot be reached (network/connectivity)."""
    pass

class TranscriptionTimeoutError(TranscriptionError):
    """Raised when the transcription request times out."""
    pass

class TranscriptionConfigurationError(TranscriptionError):
    """Raised when the transcription provider is misconfigured."""
    pass

class TranscriptionProcessingError(TranscriptionError):
    """Raised when the transcription engine fails to process the media."""
    pass

class LanguageNotSupportedError(TranscriptionError):
    """Raised when the requested language is not supported by the provider."""
    pass

class TranscriptValidationError(TranscriptionError):
    """Raised when a transcript fails structural or business validation rules."""
    pass
