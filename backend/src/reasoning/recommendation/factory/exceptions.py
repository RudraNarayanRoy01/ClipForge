class RecommendationContextFactoryError(Exception):
    """Base exception for recommendation context factory errors."""
    pass


class ContextConstructionError(RecommendationContextFactoryError):
    """Raised when context construction fails."""
    pass


class MetricValidationError(ContextConstructionError):
    """Raised when a metric fails validation."""
    pass


class AttributeValidationError(ContextConstructionError):
    """Raised when an attribute fails validation."""
    pass
