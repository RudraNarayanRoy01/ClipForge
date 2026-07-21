from src.reasoning.recommendation.models import (
    RecommendationResult,
    RecommendationDecision,
    RecommendationReasoning,
    RecommendationPriority,
    SuggestedAction,
    RecommendationConfidence
)
from src.reasoning.recommendation.policy.interfaces import IRecommendationPolicy
from src.reasoning.recommendation.policy.exceptions import RecommendationInterpretationError


class DefaultRecommendationPolicy(IRecommendationPolicy):
    """
    Default implementation of IRecommendationPolicy.
    Interprets RecommendationResult into a cohesive Recommendation business decision.
    """

    def interpret(self, result: RecommendationResult) -> RecommendationDecision:
        try:
            return self._interpret_decision(result)
        except Exception as e:
            raise RecommendationInterpretationError(
                f"Failed to interpret recommendation result for request {result.request_id}"
            ) from e

    def _interpret_decision(self, result: RecommendationResult) -> RecommendationDecision:
        """
        Translates deterministic evaluation logic (RecommendationResult) 
        into business interpretation (RecommendationDecision).
        """
        if not result.is_successful:
            return RecommendationDecision(
                primary_action=SuggestedAction.ESCALATE,
                priority=RecommendationPriority.CRITICAL,
                is_actionable=False,
                reasoning=RecommendationReasoning(
                    explanation="Engine failed to evaluate the recommendation request.",
                    risks=["System or context errors prevented successful evaluation."],
                    assumptions=[],
                    opportunities=[],
                    supporting_rationale=["is_successful flag in RecommendationResult is False."]
                )
            )

        matched_rules = [match for match in result.rule_matches if match.is_matched]
        
        if not matched_rules:
            return RecommendationDecision(
                primary_action=SuggestedAction.ARCHIVE,
                priority=RecommendationPriority.LOW,
                is_actionable=False,
                reasoning=RecommendationReasoning(
                    explanation="No recommendation rules matched.",
                    risks=[],
                    assumptions=["Content or context does not meet thresholds for a positive recommendation."],
                    opportunities=[],
                    supporting_rationale=["rule_matches contained no positive matches."]
                )
            )

        # Derive business priority and suggested action from the deterministic result
        priority = RecommendationPriority.NORMAL
        action = SuggestedAction.REVIEW
        
        # Interpret confidence based on the number of matching rules
        if len(matched_rules) >= 4:
            priority = RecommendationPriority.HIGH
            action = SuggestedAction.PUBLISH
        elif len(matched_rules) <= 1:
            priority = RecommendationPriority.LOW

        rationale = [f"Matched rule: {r.description}" for r in matched_rules]

        return RecommendationDecision(
            primary_action=action,
            priority=priority,
            is_actionable=True,
            reasoning=RecommendationReasoning(
                explanation=f"Recommendation supported by {len(matched_rules)} matching rule(s).",
                risks=[],
                assumptions=["Rules reflect current business objectives."],
                opportunities=["Potentially viable content for further action."],
                supporting_rationale=rationale
            )
        )
