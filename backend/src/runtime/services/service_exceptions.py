"""
Service exceptions.
"""

class ServiceCompositionException(Exception):
    """Base exception for Service Composition errors."""
    pass

class ServiceValidationException(ServiceCompositionException):
    pass

class DuplicateServiceException(ServiceValidationException):
    pass

class InvalidServiceDescriptorException(ServiceValidationException):
    pass

class IncompleteServiceCompositionException(ServiceValidationException):
    pass

class ServiceSnapshotException(ServiceCompositionException):
    pass

class ServiceBuildException(ServiceCompositionException):
    pass

class ServiceFrozenException(ServiceCompositionException):
    pass
