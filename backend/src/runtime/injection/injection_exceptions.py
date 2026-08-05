"""
Runtime Injection Exceptions.

Defines the explicit exception hierarchy for the Runtime Dependency Injection Foundation.
"""

class InjectionException(Exception):
    """Base exception for all Runtime Injection errors."""
    pass


class InjectionValidationException(InjectionException):
    """Raised when validation of injection bindings or descriptors fails."""
    pass


class DuplicateBindingException(InjectionValidationException):
    """Raised when a duplicate binding is detected for the same interface."""
    pass


class CircularInjectionException(InjectionValidationException):
    """Raised when a circular dependency is detected in the injection graph."""
    pass


class InvalidInjectionException(InjectionValidationException):
    """Raised when an injection definition or descriptor is malformed."""
    pass


class MissingImplementationException(InjectionValidationException):
    """Raised when an interface requires an implementation that is missing."""
    pass


class InjectionCompositionException(InjectionException):
    """Raised when an operation fails on the canonical composition."""
    pass
