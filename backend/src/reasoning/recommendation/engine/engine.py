import uuid
from typing import Sequence

from ..models import RecommendationContext, RecommendationResult, RecommendationRuleMatch
from ..rules.interfaces import IRecommendationRule
from .interfaces import IRecommendationEngine
from .exceptions import RuleExecutionError


class DefaultRecommendationEngine(IRecommendationEngine):
    """
    Default implementation of IRecommendationEngine.
    Iterates over injected Recommendation Rules, collects their matches,
    and assembles the final deterministic RecommendationResult.
    
    This engine remains agnostic to the number and types of injected rules,
    ensuring it is closed for modification but open for extension.
    """

    def __init__(self, rules: Sequence[IRecommendationRule]):
        """
        Initializes the engine with a collection of recommendation rules.
        
        Args:
            rules: A sequence of rule abstractions to execute.
        """
        self._rules = rules

    def evaluate(self, request_id: uuid.UUID, context: RecommendationContext) -> RecommendationResult:
        """
        Executes every injected Recommendation Rule against the context.
        Collects all RuleMatches and constructs a RecommendationResult.

        Exceptions from rules are caught and wrapped in a RuleExecutionError
        to preserve context while enforcing deterministic failure behavior.
        """
        rule_matches = []

        for rule in self._rules:
            try:
                match: RecommendationRuleMatch = rule.evaluate(context)
                rule_matches.append(match)
            except Exception as e:
                # Wrap rule execution failures using exception chaining
                raise RuleExecutionError(f"Failed to execute recommendation rule: {rule.__class__.__name__}") from e

        # The engine does not produce a RecommendationDecision or RecommendationReasoning.
        # It assembles the deterministic execution outcome.
        return RecommendationResult(
            request_id=request_id,
            is_successful=True,
            rule_matches=rule_matches
        )
