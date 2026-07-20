from typing import Protocol

from backend.src.reasoning.recommendation.models import (
    RecommendationRequest,
    RecommendationInput,
    Recommendation
)


class IRecommendationService(Protocol):
    """
    Defines the contract for the application orchestrator of the Recommendation pipeline.
    Coordinates context construction, rule evaluation, and policy interpretation.
    """

    def generate_recommendation(
        self,
        request: RecommendationRequest,
        input_data: RecommendationInput
    ) -> Recommendation:
        """
        Orchestrates the generation of a recommendation for the given request.

        Args:
            request: The immutable application request.
            input_data: The raw domain inputs required for evaluation.

        Returns:
            Recommendation: The finalized recommendation aggregate.

        Raises:
            RecommendationServiceError: If the orchestration fails at any stage.
        """
        ...
