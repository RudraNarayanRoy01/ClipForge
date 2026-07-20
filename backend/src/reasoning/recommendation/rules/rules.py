import uuid
from typing import Optional, Set

from .interfaces import IRecommendationRule
from .exceptions import RuleEvaluationError
from ..models import RecommendationContext, RecommendationRuleMatch


class DeadlineRule(IRecommendationRule):
    """
    Evaluates if the context meets the critical deadline threshold.
    """
    def __init__(self, threshold_days: float = 3.0, rule_id: Optional[uuid.UUID] = None):
        self.threshold_days = threshold_days
        self.rule_id = rule_id or uuid.uuid4()

    def evaluate(self, context: RecommendationContext) -> RecommendationRuleMatch:
        try:
            days = context.metrics.days_to_deadline
            is_matched = days is not None and days <= self.threshold_days
            return RecommendationRuleMatch(
                rule_id=self.rule_id,
                description=f"Evaluates if days_to_deadline is <= {self.threshold_days}",
                is_matched=is_matched
            )
        except Exception as e:
            raise RuleEvaluationError(f"Failed to evaluate DeadlineRule: {e}") from e


class RewardRule(IRecommendationRule):
    """
    Evaluates if the context meets the high reward threshold.
    """
    def __init__(self, threshold: float = 80.0, rule_id: Optional[uuid.UUID] = None):
        self.threshold = threshold
        self.rule_id = rule_id or uuid.uuid4()

    def evaluate(self, context: RecommendationContext) -> RecommendationRuleMatch:
        try:
            reward = context.metrics.estimated_reward
            is_matched = reward is not None and reward >= self.threshold
            return RecommendationRuleMatch(
                rule_id=self.rule_id,
                description=f"Evaluates if estimated_reward is >= {self.threshold}",
                is_matched=is_matched
            )
        except Exception as e:
            raise RuleEvaluationError(f"Failed to evaluate RewardRule: {e}") from e


class ConfidenceRule(IRecommendationRule):
    """
    Evaluates if the context meets the required confidence score.
    """
    def __init__(self, threshold: float = 0.8, rule_id: Optional[uuid.UUID] = None):
        self.threshold = threshold
        self.rule_id = rule_id or uuid.uuid4()

    def evaluate(self, context: RecommendationContext) -> RecommendationRuleMatch:
        try:
            confidence = context.metrics.confidence_score
            is_matched = confidence is not None and confidence >= self.threshold
            return RecommendationRuleMatch(
                rule_id=self.rule_id,
                description=f"Evaluates if confidence_score is >= {self.threshold}",
                is_matched=is_matched
            )
        except Exception as e:
            raise RuleEvaluationError(f"Failed to evaluate ConfidenceRule: {e}") from e


class EffortRule(IRecommendationRule):
    """
    Evaluates if the required effort is within acceptable limits.
    """
    def __init__(self, threshold: float = 5.0, rule_id: Optional[uuid.UUID] = None):
        self.threshold = threshold
        self.rule_id = rule_id or uuid.uuid4()

    def evaluate(self, context: RecommendationContext) -> RecommendationRuleMatch:
        try:
            effort = context.metrics.estimated_effort
            is_matched = effort is not None and effort <= self.threshold
            return RecommendationRuleMatch(
                rule_id=self.rule_id,
                description=f"Evaluates if estimated_effort is <= {self.threshold}",
                is_matched=is_matched
            )
        except Exception as e:
            raise RuleEvaluationError(f"Failed to evaluate EffortRule: {e}") from e


class PlatformSuitabilityRule(IRecommendationRule):
    """
    Evaluates if the target platform is among the supported or suitable platforms.
    """
    def __init__(self, supported_platforms: Set[str], rule_id: Optional[uuid.UUID] = None):
        self.supported_platforms = supported_platforms
        self.rule_id = rule_id or uuid.uuid4()

    def evaluate(self, context: RecommendationContext) -> RecommendationRuleMatch:
        try:
            platform = context.attributes.target_platform
            is_matched = platform is not None and platform in self.supported_platforms
            return RecommendationRuleMatch(
                rule_id=self.rule_id,
                description=f"Evaluates if target_platform is in {self.supported_platforms}",
                is_matched=is_matched
            )
        except Exception as e:
            raise RuleEvaluationError(f"Failed to evaluate PlatformSuitabilityRule: {e}") from e


class RiskRule(IRecommendationRule):
    """
    Evaluates if the risk level is below the maximum acceptable threshold.
    """
    def __init__(self, threshold: float = 0.5, rule_id: Optional[uuid.UUID] = None):
        self.threshold = threshold
        self.rule_id = rule_id or uuid.uuid4()

    def evaluate(self, context: RecommendationContext) -> RecommendationRuleMatch:
        try:
            risk = context.metrics.risk_score
            is_matched = risk is not None and risk <= self.threshold
            return RecommendationRuleMatch(
                rule_id=self.rule_id,
                description=f"Evaluates if risk_score is <= {self.threshold}",
                is_matched=is_matched
            )
        except Exception as e:
            raise RuleEvaluationError(f"Failed to evaluate RiskRule: {e}") from e
