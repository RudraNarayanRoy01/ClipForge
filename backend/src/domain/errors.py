class DomainError(Exception):
    """Base exception for all domain errors."""
    pass

class PlanningError(DomainError):
    """Base exception for planning logic errors."""
    pass

class ValidationError(DomainError):
    """Raised when domain entities or planning artifacts are malformed or internally inconsistent."""
    pass

class PersistenceError(DomainError):
    """Raised when the repository fails to save or load an entity."""
    pass

class InfrastructureError(DomainError):
    """Raised when external dependencies (like AI providers or databases) are unreachable or fail."""
    pass

class DependencyError(DomainError):
    """Raised when injected dependencies are missing, misconfigured, or fail to resolve."""
    pass
