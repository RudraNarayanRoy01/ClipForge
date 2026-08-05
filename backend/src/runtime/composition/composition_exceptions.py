from enum import Enum

class CompositionException(Exception):
    """Base exception for all Runtime Composition errors."""
    pass

class CompositionValidationException(CompositionException):
    """Raised when validation of the composition fails (e.g., missing dependencies)."""
    pass

class CompositionBuildException(CompositionException):
    """Raised when the composition cannot be built."""
    pass

class IncompleteCompositionException(CompositionException):
    """Raised when the composition is incomplete."""
    pass

class CompositionFrozenException(CompositionException):
    """Raised when an attempt is made to mutate a frozen composition."""
    pass
