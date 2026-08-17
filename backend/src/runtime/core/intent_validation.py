from typing import Any
from .intent import ExecutionIntent

class IntentValidationError(Exception):
    """
    Raised when an ExecutionIntent violates the Runtime's
    structural validation contract.
    """
    pass

class ExecutionIntentValidator:
    """
    Validates the structure of the ExecutionIntent boundary before planning.
    """

    def validate(self, intent: Any) -> None:
        if not isinstance(intent, ExecutionIntent):
            raise IntentValidationError("intent must be an ExecutionIntent")

        if not isinstance(intent.capability_id, str) or not intent.capability_id.strip():
            raise IntentValidationError("intent.capability_id must be a non-empty string")

        if intent.output_contract is not None:
            if not isinstance(intent.output_contract, str) or not intent.output_contract.strip():
                raise IntentValidationError("intent.output_contract must be None or a non-empty string")
