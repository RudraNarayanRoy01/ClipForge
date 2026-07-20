import uuid
from typing import List, Optional, Protocol

from ..models import RecommendationContext


class IRecommendationContextFactory(Protocol):
    """
    Protocol for constructing RecommendationContext instances.
    Owns the construction of RecommendationMetrics and RecommendationAttributes.
    """

    def create_context(
        self,
        context_id: Optional[uuid.UUID] = None,
        facts: Optional[List[str]] = None,
        days_to_deadline: Optional[float] = None,
        estimated_reward: Optional[float] = None,
        confidence_score: Optional[float] = None,
        estimated_effort: Optional[float] = None,
        risk_score: Optional[float] = None,
        target_platform: Optional[str] = None,
        content_category: Optional[str] = None
    ) -> RecommendationContext:
        """
        Creates a fully populated RecommendationContext from raw inputs.
        
        This factory centralizes:
        - Construction of RecommendationContext
        - Construction of RecommendationMetrics
        - Construction of RecommendationAttributes
        - Validation and normalization of raw inputs
        """
        ...
