import abc

from backend.src.reasoning.recommendation.models import (
    RecommendationResult,
    RecommendationDecision
)


class IRecommendationPolicy(abc.ABC):
    """
    Defines the contract for interpreting a deterministic RecommendationResult 
    into a business-facing RecommendationDecision.
    
    The Recommendation Policy performs business interpretation.
    It does not execute Recommendation Rules or evaluate RecommendationContext.
    It transforms deterministic evaluation into business decisions.
    """

    @abc.abstractmethod
    def interpret(self, result: RecommendationResult) -> RecommendationDecision:
        """
        Interprets the deterministic evaluation result into a business recommendation decision.

        Args:
            result (RecommendationResult): The output from the recommendation engine.

        Returns:
            RecommendationDecision: The finalized recommendation decision containing the business interpretation.
            
        Raises:
            RecommendationInterpretationError: If the interpretation fails.
        """
        pass
