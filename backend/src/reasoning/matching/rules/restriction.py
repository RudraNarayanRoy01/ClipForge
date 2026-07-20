from src.reasoning.matching.rules.interfaces import (
    IMatchingRule,
    MatchingContext,
    RuleEvaluationResult,
)
from src.reasoning.knowledge.models import KnowledgeCategory
from src.reasoning.matching.models import MatchConfidence


class RestrictionMatchingRule(IMatchingRule):
    """
    Evaluates if the target violates any explicit content restrictions of the campaign.
    """

    def evaluate(self, context: MatchingContext) -> RuleEvaluationResult:
        campaign = context.campaign
        
        campaign_restrictions = campaign.rules.content_restrictions if campaign.rules else []
        
        if not campaign_restrictions:
            return RuleEvaluationResult(
                is_matched=True,
                evidence=["Campaign does not have specific content restrictions."],
                explanation="No restriction violations possible.",
                confidence=MatchConfidence.HIGH,
            )

        # Look for target's known restrictions or flags
        restriction_knowledge = [
            k for k in context.knowledge
            if k.category == KnowledgeCategory.RESTRICTION
        ]

        if not restriction_knowledge:
            return RuleEvaluationResult(
                is_matched=True,
                evidence=["Target has no known restriction flags."],
                explanation="Target does not demonstrably violate any campaign restrictions.",
                confidence=MatchConfidence.MEDIUM,
            )

        # Deterministic check for intersections between campaign restrictions and known target restrictions
        violations = []
        for restriction in campaign_restrictions:
            for k in restriction_knowledge:
                if restriction.lower() in k.value.lower() or k.value.lower() in restriction.lower():
                    violations.append(f"Target flag '{k.value}' conflicts with campaign restriction '{restriction}'")

        if violations:
            return RuleEvaluationResult(
                is_matched=False,
                evidence=violations,
                explanation="Target violates one or more campaign content restrictions.",
                confidence=MatchConfidence.HIGH,
            )

        return RuleEvaluationResult(
            is_matched=True,
            evidence=["Target's known restriction flags do not conflict with campaign requirements."],
            explanation="No restriction violations detected.",
            confidence=MatchConfidence.HIGH,
        )
