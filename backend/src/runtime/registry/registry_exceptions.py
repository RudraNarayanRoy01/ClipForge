class RegistryException(Exception):
    """Base exception for all Registry related errors."""
    pass

class DuplicateComponentException(RegistryException):
    """Raised when attempting to register a component with an already existing ID or Name."""
    pass

class UnknownComponentException(RegistryException):
    """Raised when attempting to lookup or interact with a component that does not exist in the registry."""
    pass

class RegistryFrozenException(RegistryException):
    """Raised when attempting to modify a registry that has been frozen."""
    pass

class InvalidComponentException(RegistryException):
    """Raised when a component is deemed invalid (e.g., missing required metadata)."""
    pass

class RegistryConsistencyException(RegistryException):
    """Raised when the registry detects an internal consistency error."""
    pass
