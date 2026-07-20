class RecommendationPolicyError(Exception):
    """Base exception for all recommendation policy errors."""
    pass


class RecommendationInterpretationError(RecommendationPolicyError):
    """Raised when the policy fails to interpret a RecommendationResult."""
    pass
