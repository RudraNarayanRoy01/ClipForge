from abc import ABC, abstractmethod
from ..models import RecommendationContext, RecommendationRuleMatch

class IRecommendationRule(ABC):
    """
    Contract for a deterministic recommendation rule.
    A rule evaluates exactly one dimension/concern.
    It does not prioritize, interpret, or recommend.
    """
    
    @abstractmethod
    def evaluate(self, context: RecommendationContext) -> RecommendationRuleMatch:
        """
        Evaluates the context and returns a deterministic rule match.
        """
        pass
