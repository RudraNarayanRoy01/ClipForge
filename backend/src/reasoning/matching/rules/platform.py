from typing import List
from src.reasoning.matching.rules.interfaces import (
    IMatchingRule,
    MatchingContext,
    RuleEvaluationResult,
)
from src.reasoning.knowledge.models import KnowledgeCategory
from src.reasoning.matching.models import MatchConfidence


class PlatformMatchingRule(IMatchingRule):
    """
    Evaluates if the campaign's target platforms align with the known platform capabilities
    of the target entity (as represented in the knowledge context).
    """

    def evaluate(self, context: MatchingContext) -> RuleEvaluationResult:
        if not context.campaign.platforms:
            return RuleEvaluationResult(
                is_matched=True,
                evidence=[],
                explanation="Campaign has no specific platform requirements.",
                confidence=MatchConfidence.HIGH,
            )

        # Extract platform knowledge
        target_platforms = [
            k.value.lower()
            for k in context.knowledge
            if k.category == KnowledgeCategory.PLATFORM
        ]

        if not target_platforms:
            return RuleEvaluationResult(
                is_matched=False,
                evidence=["No platform knowledge entries found for target."],
                explanation="Cannot verify platform compatibility due to missing platform knowledge.",
                confidence=MatchConfidence.LOW,
            )

        matched_platforms: List[str] = []
        missing_platforms: List[str] = []

        for req_platform in context.campaign.platforms:
            if req_platform.lower() in target_platforms:
                matched_platforms.append(req_platform)
            else:
                missing_platforms.append(req_platform)

        # For this rule, we require at least one matching platform
        # Unless strict constraints say otherwise. Here we check if any platform matches.
        is_matched = len(matched_platforms) > 0

        evidence = []
        if matched_platforms:
            evidence.append(f"Matched platforms: {', '.join(matched_platforms)}")
        if missing_platforms:
            evidence.append(f"Missing platforms: {', '.join(missing_platforms)}")

        if is_matched:
            explanation = "Target supports at least one of the campaign's required platforms."
        else:
            explanation = "Target does not support any of the campaign's required platforms."

        return RuleEvaluationResult(
            is_matched=is_matched,
            evidence=evidence,
            explanation=explanation,
            confidence=MatchConfidence.HIGH,
        )
