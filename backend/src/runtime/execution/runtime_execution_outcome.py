from enum import Enum

class RuntimeExecutionOutcome(str, Enum):
    """
    Terminal execution outcome.
    
    REJECTED belongs before execution.
    RuntimeExecutionResult exists only for an execution attempt.
    Cancellation is a terminal execution outcome.
    """
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
