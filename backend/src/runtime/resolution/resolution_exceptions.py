class ResolutionException(Exception):
    """Base exception for all Runtime Resolution errors."""
    pass

class ResolutionBuildException(ResolutionException):
    """Raised when resolution building fails."""
    pass

class ResolutionValidationException(ResolutionException):
    """Raised when resolution validation fails."""
    pass

class ResolutionOrderingException(ResolutionException):
    """Raised when deterministic ordering cannot be computed."""
    pass

class ResolutionCycleException(ResolutionException):
    """Raised when a dependency cycle is detected."""
    pass

class ResolutionFrozenException(ResolutionException):
    """Raised when attempting to mutate an immutable resolution artifact."""
    pass
