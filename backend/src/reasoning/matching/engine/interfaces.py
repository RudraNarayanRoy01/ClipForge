from abc import ABC, abstractmethod

from src.reasoning.matching.models import MatchResult
from src.reasoning.matching.rules.interfaces import MatchingContext


class IMatchingEngine(ABC):
    """
    Coordinates matching rules to assemble a MatchResult.
    Performs no business policy or evaluation itself.
    """

    @abstractmethod
    def evaluate(self, context: MatchingContext) -> MatchResult:
        """
        Executes registered matching rules and assembles the deterministic MatchResult.

        Args:
            context (MatchingContext): The immutable domain state.

        Returns:
            MatchResult: The outcome of the matching evaluation.
        """
        pass
