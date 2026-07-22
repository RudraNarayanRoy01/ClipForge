from typing import Any, Dict, Optional

class RenderJobValidationError(Exception):
    """Raised when a RenderJob fails application-level validation."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InvalidRenderJobTransitionError(Exception):
    """Raised when an illegal lifecycle transition is attempted on a RenderJob."""
    
    def __init__(self, current_status: str, target_status: str, message: Optional[str] = None):
        self.current_status = current_status
        self.target_status = target_status
        self.message = message or f"Invalid transition from {current_status} to {target_status}"
        super().__init__(self.message)
