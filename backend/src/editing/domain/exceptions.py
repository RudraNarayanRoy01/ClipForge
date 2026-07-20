from src.domain.errors import DomainError


class UnsupportedTimelineOperationError(DomainError):
    """Raised when a timeline operation type is not supported by the executor."""
    pass
