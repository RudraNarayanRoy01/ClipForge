"""
Bootstrap Exceptions.

Domain-specific exceptions for the Runtime Bootstrap Foundation.
"""


class RuntimeBootstrapException(Exception):
    """Base exception for all Runtime Bootstrap errors."""
    pass


class BootstrapValidationException(RuntimeBootstrapException):
    """Raised when the Bootstrap structure fails structural validation."""
    pass


class BootstrapGraphException(RuntimeBootstrapException):
    """Raised when there are issues with the Bootstrap Graph topology (e.g., cycles)."""
    pass


class BootstrapPlanException(RuntimeBootstrapException):
    """Raised when there are issues with Bootstrap Planning (e.g., invalid ordering)."""
    pass


class BootstrapMetadataException(RuntimeBootstrapException):
    """Raised when there are issues with Bootstrap Metadata."""
    pass
