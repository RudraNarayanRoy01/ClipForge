from abc import ABC, abstractmethod

from src.editing.domain.models.state import TimelineState
from src.editing.domain.models.validation import ValidationResult


class ITimelineValidationService(ABC):
    """
    Evaluates whether a TimelineState satisfies the editing domain's structural invariants.

    The validation service performs evaluation only.
    It does not execute operations.
    It does not repair timelines.
    It does not mutate TimelineState.
    """

    @abstractmethod
    def validate(self, timeline_state: TimelineState) -> ValidationResult:
        """
        Validates the structure, metadata, constraints, and time ranges of a TimelineState.

        Args:
            timeline_state: The state to validate.

        Returns:
            A structured, immutable ValidationResult.
        """
        pass
