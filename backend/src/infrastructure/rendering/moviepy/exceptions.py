from typing import Dict, Any, Tuple
from src.application.execution_models import RenderFailureCategory

class MoviePyExceptionTranslator:
    """
    Utility component responsible for translating backend-specific exceptions
    (e.g., MoviePy, OS/IO errors) into backend-neutral failure categories.
    
    This translation remains explicit and reusable rather than being hidden
    behind decorators, ensuring clear architectural boundaries.
    """
    
    @classmethod
    def translate(cls, exception: Exception) -> Tuple[RenderFailureCategory, str, Dict[str, Any]]:
        """
        Translates a raw exception into neutral failure components.
        
        Args:
            exception: The raw exception raised by the backend.
            
        Returns:
            Tuple containing:
            - RenderFailureCategory: The mapped category of the failure.
            - str: A generic message safe for the application layer.
            - Dict[str, Any]: Detailed diagnostic information.
        """
        details: Dict[str, Any] = {
            "error_type": type(exception).__name__,
            "error_message": str(exception),
            "backend": "MoviePy"
        }
        
        if isinstance(exception, FileNotFoundError):
            category = RenderFailureCategory.RESOURCE_EXHAUSTED
            message = "Required asset not found on disk."
        elif isinstance(exception, PermissionError):
            category = RenderFailureCategory.RESOURCE_EXHAUSTED
            message = "Permission denied when accessing required asset."
        elif isinstance(exception, ValueError):
            category = RenderFailureCategory.VALIDATION_REQUIRED
            message = "Invalid parameters or unsupported asset provided to the rendering backend."
        elif isinstance(exception, (OSError, IOError)):
            # MoviePy often raises OSError when it cannot read a file or probe it via ffmpeg
            category = RenderFailureCategory.RESOURCE_EXHAUSTED
            message = "An IO or OS error occurred while loading or processing media."
        else:
            category = RenderFailureCategory.BACKEND_FAILURE
            message = "An unexpected rendering backend error occurred."
            
        return category, message, details
