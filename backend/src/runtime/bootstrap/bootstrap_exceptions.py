from typing import Optional, Dict, Any
from .runtime_state import RuntimeState


class RuntimeBootstrapException(Exception):
    """Base exception for all Runtime Bootstrap failures."""
    
    def __init__(self, message: str, state: Optional[RuntimeState] = None, reason: Optional[str] = None, diagnostics: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.state = state
        self.reason = reason
        self.diagnostics = diagnostics or {}


class BootstrapInitializationException(RuntimeBootstrapException):
    """Raised when Runtime initialization fails."""
    pass


class BootstrapValidationException(RuntimeBootstrapException):
    """Raised when Runtime validation fails."""
    pass


class BootstrapShutdownException(RuntimeBootstrapException):
    """Raised when Runtime shutdown fails."""
    pass


class InvalidRuntimeStateTransitionException(RuntimeBootstrapException):
    """Raised when an illegal state transition is attempted."""
    
    def __init__(self, current_state: RuntimeState, attempted_state: RuntimeState, message: Optional[str] = None):
        msg = message or f"Illegal Runtime state transition from {current_state.name} to {attempted_state.name}"
        super().__init__(msg, state=current_state, reason="Invalid state transition")
        self.current_state = current_state
        self.attempted_state = attempted_state
