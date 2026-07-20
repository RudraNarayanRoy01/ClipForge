import uuid
from typing import List, Optional

from src.reasoning.recommendation.models import (
    RecommendationContext,
    RecommendationMetrics,
    RecommendationAttributes
)
from .interfaces import IRecommendationContextFactory
from .exceptions import ContextConstructionError, MetricValidationError, AttributeValidationError


class DefaultRecommendationContextFactory(IRecommendationContextFactory):
    """
    Default implementation for RecommendationContext factory.
    Centralizes validation, normalization, and default values.
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
        
        try:
            # 1. Normalize and validate facts
            normalized_facts = self._normalize_facts(facts)
            
            # 2. Construct Metrics
            metrics = self._create_metrics(
                days_to_deadline=days_to_deadline,
                estimated_reward=estimated_reward,
                confidence_score=confidence_score,
                estimated_effort=estimated_effort,
                risk_score=risk_score
            )
            
            # 3. Construct Attributes
            attributes = self._create_attributes(
                target_platform=target_platform,
                content_category=content_category
            )
            
            # 4. Construct Context
            return RecommendationContext(
                context_id=context_id or uuid.uuid4(),
                facts=normalized_facts,
                metrics=metrics,
                attributes=attributes
            )
        except (MetricValidationError, AttributeValidationError) as e:
            raise ContextConstructionError(f"Validation failed during context construction: {str(e)}") from e
        except Exception as e:
            raise ContextConstructionError(f"Unexpected error constructing context: {str(e)}") from e

    def _normalize_facts(self, facts: Optional[List[str]]) -> List[str]:
        if not facts:
            return []
        return [str(fact).strip() for fact in facts if fact and str(fact).strip()]

    def _create_metrics(
        self,
        days_to_deadline: Optional[float],
        estimated_reward: Optional[float],
        confidence_score: Optional[float],
        estimated_effort: Optional[float],
        risk_score: Optional[float]
    ) -> RecommendationMetrics:
        
        # Validation for confidence_score
        if confidence_score is not None:
            if not (0.0 <= confidence_score <= 1.0):
                raise MetricValidationError(f"confidence_score must be between 0.0 and 1.0, got {confidence_score}")
                
        # Validation for risk_score
        if risk_score is not None:
            if not (0.0 <= risk_score <= 1.0):
                raise MetricValidationError(f"risk_score must be between 0.0 and 1.0, got {risk_score}")
                
        # Optional validation for effort and reward
        if estimated_effort is not None and estimated_effort < 0:
            raise MetricValidationError(f"estimated_effort cannot be negative, got {estimated_effort}")
            
        if estimated_reward is not None and estimated_reward < 0:
            raise MetricValidationError(f"estimated_reward cannot be negative, got {estimated_reward}")

        return RecommendationMetrics(
            days_to_deadline=days_to_deadline,
            estimated_reward=estimated_reward,
            confidence_score=confidence_score,
            estimated_effort=estimated_effort,
            risk_score=risk_score
        )

    def _create_attributes(
        self,
        target_platform: Optional[str],
        content_category: Optional[str]
    ) -> RecommendationAttributes:
        
        normalized_platform = target_platform.strip().lower() if target_platform and str(target_platform).strip() else None
        normalized_category = content_category.strip().lower() if content_category and str(content_category).strip() else None
        
        return RecommendationAttributes(
            target_platform=normalized_platform,
            content_category=normalized_category
        )
