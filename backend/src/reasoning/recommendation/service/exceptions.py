class RecommendationServiceError(Exception):
    """
    Base exception for errors raised by the Recommendation Service.
    Wraps underlying errors (e.g. ContextConstructionError, engine/policy errors) using exception chaining.
    """
    pass
