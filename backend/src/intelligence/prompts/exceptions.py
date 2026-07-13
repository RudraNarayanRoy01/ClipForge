class PromptError(Exception):
    """Base class for all prompt framework exceptions."""
    pass

class PromptNotFoundError(PromptError):
    """Raised when a requested prompt file does not exist."""
    pass

class PromptValidationError(PromptError):
    """Raised when a prompt template fails validation (e.g. missing variables, malformed metadata)."""
    pass
