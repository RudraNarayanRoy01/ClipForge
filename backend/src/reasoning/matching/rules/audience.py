from src.reasoning.matching.rules.interfaces import (
    IMatchingRule,
    MatchingContext,
    RuleEvaluationResult,
)
from src.reasoning.matching.models import MatchConfidence


class AudienceMatchingRule(IMatchingRule):
    """
    Evaluates if the target's expected audience aligns with the campaign's target audience.
    """

    def evaluate(self, context: MatchingContext) -> RuleEvaluationResult:
        campaign = context.campaign

        # In a fully fleshed domain, Campaign would have explicit audience_requirements.
        # For this rule, we fall back to the campaign summary or rules to see if an audience is implied.
        has_audience_constraints = (
            campaign.summary and "audience" in campaign.summary.requirements.lower()
        )

        if not has_audience_constraints:
            return RuleEvaluationResult(
                is_matched=True,
                evidence=["Campaign does not specify strict audience requirements."],
                explanation="Audience matching successful by default.",
                confidence=MatchConfidence.HIGH,
            )

        # Look for audience-related knowledge in CREATOR or CAMPAIGN knowledge.
        # We assume subject="audience" captures this.
        audience_knowledge = [
            k for k in context.knowledge
            if k.subject.lower() == "audience"
        ]

        if not audience_knowledge:
            return RuleEvaluationResult(
                is_matched=False,
                evidence=["Campaign implies audience constraints, but target audience is unknown."],
                explanation="Cannot verify audience compatibility.",
                confidence=MatchConfidence.MEDIUM,
            )

        # Deterministic check: we just ensure the knowledge exists and is documented.
        # Deep semantic audience matching is handled prior to rules (via embeddings) or left to AI.
        # This deterministic rule just validates presence and absence of explicit conflicts.
        evidence = [f"Found documented audience knowledge: {k.value}" for k in audience_knowledge]

        return RuleEvaluationResult(
            is_matched=True,
            evidence=evidence,
            explanation="Target has documented audience profiles that can be leveraged.",
            confidence=MatchConfidence.MEDIUM,
        )
