from src.reasoning.matching.rules.interfaces import (
    IMatchingRule,
    MatchingContext,
    RuleEvaluationResult,
)
from src.reasoning.knowledge.models import KnowledgeCategory
from src.reasoning.matching.models import MatchConfidence


class CreatorMatchingRule(IMatchingRule):
    """
    Evaluates if the creator's profile (from knowledge) aligns with any creator-specific
    requirements in the campaign.
    """

    def evaluate(self, context: MatchingContext) -> RuleEvaluationResult:
        creator_knowledge = [
            k for k in context.knowledge
            if k.category == KnowledgeCategory.CREATOR
        ]

        if not creator_knowledge:
            return RuleEvaluationResult(
                is_matched=True,
                evidence=["No specific creator knowledge available."],
                explanation="No creator constraints known for the target.",
                confidence=MatchConfidence.LOW,
            )

        # In a fully fleshed domain, Campaign would have explicit creator_requirements.
        # Here we do a deterministic check on whether the target creator's region is allowed.
        allowed_regions = context.campaign.rules.allowed_regions if context.campaign.rules else []
        
        if not allowed_regions:
            return RuleEvaluationResult(
                is_matched=True,
                evidence=["Campaign does not specify geographic creator restrictions."],
                explanation="Creator matching successful by default.",
                confidence=MatchConfidence.HIGH,
            )

        region_knowledge = [
            k for k in creator_knowledge
            if k.subject.lower() == "region" or k.subject.lower() == "location"
        ]

        if not region_knowledge:
            return RuleEvaluationResult(
                is_matched=False,
                evidence=["Campaign requires specific regions, but target creator region is unknown."],
                explanation="Cannot verify region compliance.",
                confidence=MatchConfidence.MEDIUM,
            )

        creator_region = region_knowledge[0].value.lower()
        matched_region = any(
            allowed.lower() in creator_region or creator_region in allowed.lower()
            for allowed in allowed_regions
        )

        if matched_region:
            return RuleEvaluationResult(
                is_matched=True,
                evidence=[f"Creator region '{creator_region}' matches allowed regions."],
                explanation="Creator geographic profile aligns with campaign.",
                confidence=MatchConfidence.HIGH,
            )

        return RuleEvaluationResult(
            is_matched=False,
            evidence=[f"Creator region '{creator_region}' not in allowed regions: {allowed_regions}"],
            explanation="Creator does not meet campaign geographic requirements.",
            confidence=MatchConfidence.HIGH,
        )
