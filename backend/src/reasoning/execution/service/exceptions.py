class ExecutionServiceError(Exception):
    """Base exception for Execution Service."""
    pass


class ExecutionOrchestrationError(ExecutionServiceError):
    """Raised when the service fails to orchestrate the pipeline due to unhandled component errors."""
    pass
