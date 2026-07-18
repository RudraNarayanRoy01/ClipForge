from src.reasoning.recommendation.models import (
    RecommendationDecision,
    RecommendationConfidence,
    RecommendationReason,
    RecommendationRationale,
    Recommendation
)
from src.reasoning.recommendation.interfaces import IRecommendationSynthesisEngine
from src.reasoning.recommendation.engine import DefaultRecommendationSynthesisEngine

def create_recommendation_engine() -> IRecommendationSynthesisEngine:
    """
    Factory function to create the standard Recommendation Synthesis Engine 
    with the default policy.
    """
    return DefaultRecommendationSynthesisEngine()

__all__ = [
    "RecommendationDecision",
    "RecommendationConfidence",
    "RecommendationReason",
    "RecommendationRationale",
    "Recommendation",
    "IRecommendationSynthesisEngine",
    "create_recommendation_engine",
]
