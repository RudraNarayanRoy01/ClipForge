class ComposerError(Exception):
    """Base exception for Execution Composer errors."""
    pass


class CompositionInputError(ComposerError):
    """Raised when the inputs to the composer are invalid, incomplete, or mismatched."""
    pass
