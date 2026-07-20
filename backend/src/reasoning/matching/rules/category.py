from src.reasoning.matching.rules.interfaces import (
    IMatchingRule,
    MatchingContext,
    RuleEvaluationResult,
)
from src.reasoning.knowledge.models import KnowledgeCategory
from src.reasoning.matching.models import MatchConfidence


class CategoryMatchingRule(IMatchingRule):
    """
    Evaluates alignment between the campaign's context (e.g., brand, industry)
    and the target's known campaign or category affinities.
    """

    def evaluate(self, context: MatchingContext) -> RuleEvaluationResult:
        campaign = context.campaign
        
        if not campaign.brand and not campaign.title:
            return RuleEvaluationResult(
                is_matched=True,
                evidence=[],
                explanation="Campaign lacks brand or category identifiers to match against.",
                confidence=MatchConfidence.LOW,
            )

        # Extract relevant category/campaign knowledge
        category_knowledge = [
            k for k in context.knowledge
            if k.category == KnowledgeCategory.CAMPAIGN
        ]

        if not category_knowledge:
            return RuleEvaluationResult(
                is_matched=True,  # Default allow if no restrictive knowledge
                evidence=["No category/campaign knowledge available."],
                explanation="Target has no specific category constraints or affinities.",
                confidence=MatchConfidence.MEDIUM,
            )

        # Basic deterministic check: Does the target have explicit knowledge related to the campaign's brand?
        brand_mentions = [
            k for k in category_knowledge 
            if campaign.brand and campaign.brand.lower() in k.value.lower()
        ]

        if brand_mentions:
            return RuleEvaluationResult(
                is_matched=True,
                evidence=[f"Target has positive association with brand '{campaign.brand}': {brand_mentions[0].value}"],
                explanation="Strong alignment found with campaign brand.",
                confidence=MatchConfidence.HIGH,
            )

        return RuleEvaluationResult(
            is_matched=True,
            evidence=["No direct brand conflicts or alignments found."],
            explanation="Category alignment is neutral.",
            confidence=MatchConfidence.MEDIUM,
        )
