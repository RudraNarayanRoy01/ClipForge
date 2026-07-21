from dataclasses import dataclass, field
from typing import Tuple

@dataclass(frozen=True)
class ValidationResult:
    """
    Generic result of a validation operation across the platform.
    Provides immutable validation status alongside informative messages and errors.
    """
    is_valid: bool
    errors: Tuple[str, ...] = field(default_factory=tuple)
    messages: Tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def success(cls, messages: Tuple[str, ...] = ()) -> "ValidationResult":
        """Factory for a successful validation result."""
        return cls(is_valid=True, messages=messages)

    @classmethod
    def failure(cls, errors: Tuple[str, ...], messages: Tuple[str, ...] = ()) -> "ValidationResult":
        """Factory for a failed validation result."""
        return cls(is_valid=False, errors=errors, messages=messages)
