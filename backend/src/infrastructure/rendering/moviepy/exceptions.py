from typing import Dict, Any, Tuple

class MoviePyExceptionTranslator:
    """
    Utility component responsible for translating backend-specific exceptions
    (e.g., MoviePy, OS/IO errors) into backend-neutral failure categories.
    
    This translation remains explicit and reusable rather than being hidden
    behind decorators, ensuring clear architectural boundaries.
    """
    
    @classmethod
    def translate(cls, exception: Exception) -> Tuple[str, str, Dict[str, Any]]:
        """
        Translates a raw exception into neutral failure components.
        
        Args:
            exception: The raw exception raised by the backend.
            
        Returns:
            Tuple containing:
            - str: A neutral error reason string.
            - str: A generic message safe for the application layer.
            - Dict[str, Any]: Detailed diagnostic information.
        """
        details: Dict[str, Any] = {
            "error_type": type(exception).__name__,
            "error_message": str(exception),
            "backend": "MoviePy"
        }
        
        if isinstance(exception, FileNotFoundError):
            error_reason = "resource_exhausted"
            message = "Required asset not found on disk."
        elif isinstance(exception, PermissionError):
            error_reason = "resource_exhausted"
            message = "Permission denied when accessing required asset."
        elif isinstance(exception, ValueError):
            error_reason = "validation"
            message = "Invalid parameters or unsupported asset provided to the rendering backend."
        elif isinstance(exception, (OSError, IOError)):
            # MoviePy often raises OSError when it cannot read a file or probe it via ffmpeg
            error_reason = "resource_exhausted"
            message = "An IO or OS error occurred while loading or processing media."
        else:
            error_reason = "backend_failure"
            message = "An unexpected rendering backend error occurred."
            
        details["error_reason"] = error_reason
        return error_reason, message, details
