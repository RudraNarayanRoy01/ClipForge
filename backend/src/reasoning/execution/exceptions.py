class ExecutionDomainError(Exception):
    """Base exception for the Execution Planning domain."""
    pass

class InvalidExecutionPlanError(ExecutionDomainError):
    """Raised when an execution plan is invalid."""
    pass

class ExecutionValidationError(ExecutionDomainError):
    """Raised during execution plan validation failures."""
    pass
