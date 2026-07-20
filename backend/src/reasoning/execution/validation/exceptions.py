class ExecutionValidationException(Exception):
    """
    Base exception for Execution Validation Engine failures.
    Thrown only for unexpected validator errors (e.g., invalid state),
    not for regular validation findings.
    """
    pass


class InvalidValidationInputException(ExecutionValidationException):
    """
    Thrown when the inputs provided to the validator are fundamentally invalid,
    such as None values or corrupted references.
    """
    pass
