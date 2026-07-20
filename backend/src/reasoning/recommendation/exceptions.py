class RecommendationDomainError(Exception):
    """
    Base exception for all Recommendation domain errors.
    """
    pass


class InvalidRecommendationRequestError(RecommendationDomainError):
    """
    Raised when a recommendation request is malformed or invalid.
    """
    pass


class RecommendationContextError(RecommendationDomainError):
    """
    Raised when there is an issue with the recommendation context.
    """
    pass


class ConflictingRecommendationError(RecommendationDomainError):
    """
    Raised when evaluation results in conflicting recommendations.
    """
    pass
