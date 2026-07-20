class RecommendationEngineError(Exception):
    """Base exception for all recommendation engine errors."""
    pass


class RuleExecutionError(RecommendationEngineError):
    """Raised when an injected Recommendation Rule fails to execute."""
    pass
