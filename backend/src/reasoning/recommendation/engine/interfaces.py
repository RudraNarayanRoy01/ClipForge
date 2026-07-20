import uuid
from abc import ABC, abstractmethod

from ..models import RecommendationContext, RecommendationResult


class IRecommendationEngine(ABC):
    """
    Contract for a recommendation engine.
    The engine orchestrates deterministic Recommendation Rules and assembles a RecommendationResult.
    It does not interpret business meaning, prioritize, or make decisions.
    """

    @abstractmethod
    def evaluate(self, request_id: uuid.UUID, context: RecommendationContext) -> RecommendationResult:
        """
        Executes injected Recommendation Rules against the provided context
        and assembles a deterministic RecommendationResult.

        Args:
            request_id: The ID of the request triggering this evaluation.
            context: The prepared, immutable context for rule evaluation.

        Returns:
            RecommendationResult: The deterministic evaluation output.
        """
        pass
