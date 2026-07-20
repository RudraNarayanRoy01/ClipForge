class RecommendationRuleError(Exception):
    """Base exception for all recommendation rule errors."""
    pass


class RuleEvaluationError(RecommendationRuleError):
    """Raised when a rule fails to evaluate the context."""
    pass
