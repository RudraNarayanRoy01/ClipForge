from typing import List

from src.reasoning.eligibility.models import EligibilityAssessment, EligibilityStatus
from src.reasoning.worth_it.models import WorthItAssessment, WorthItRating, AssessmentConfidence
from src.reasoning.recommendation.models import (
    RecommendationDecision,
    RecommendationConfidence,
    RecommendationReason,
    RecommendationRationale,
    Recommendation
)


class RecommendationPolicy:
    """
    Centralized decision matrix for recommendation synthesis.
    Depends solely on the structured output of prior reasoning engines.
    """

    def synthesize(
        self,
        eligibility: EligibilityAssessment,
        worth_it: WorthItAssessment
    ) -> Recommendation:
        """
        Synthesizes the assessments into a deterministic recommendation.
        """
        decision = self._determine_decision(eligibility, worth_it)
        confidence = self._determine_confidence(worth_it)
        rationale = self._build_rationale(eligibility, worth_it)
        
        return Recommendation(
            decision=decision,
            confidence=confidence,
            rationale=rationale
        )

    def _determine_decision(
        self, 
        eligibility: EligibilityAssessment, 
        worth_it: WorthItAssessment
    ) -> RecommendationDecision:
        """
        Explicit decision policy matrix mapping eligibility and worth-it 
        assessments to a final recommendation decision.
        """
        if eligibility.status == EligibilityStatus.INELIGIBLE:
            return RecommendationDecision.DO_NOT_RECOMMEND
            
        if eligibility.status == EligibilityStatus.NEEDS_REVIEW:
            return RecommendationDecision.NEEDS_HUMAN_REVIEW

        # If eligible, the decision depends on the worth-it rating
        if worth_it.overall_rating == WorthItRating.POOR:
            return RecommendationDecision.DO_NOT_RECOMMEND
            
        if worth_it.overall_rating == WorthItRating.UNKNOWN:
            return RecommendationDecision.NEEDS_HUMAN_REVIEW
            
        # For EXCELLENT, GOOD, FAIR
        return RecommendationDecision.RECOMMEND

    def _determine_confidence(
        self, 
        worth_it: WorthItAssessment
    ) -> RecommendationConfidence:
        """
        Maps the assessment confidence directly to recommendation confidence.
        """
        mapping = {
            AssessmentConfidence.HIGH: RecommendationConfidence.HIGH,
            AssessmentConfidence.MEDIUM: RecommendationConfidence.MEDIUM,
            AssessmentConfidence.LOW: RecommendationConfidence.LOW,
        }
        return mapping.get(worth_it.confidence, RecommendationConfidence.LOW)

    def _build_rationale(
        self, 
        eligibility: EligibilityAssessment, 
        worth_it: WorthItAssessment
    ) -> RecommendationRationale:
        """
        Constructs a structured rationale from the combined findings and issues.
        """
        reasons: List[RecommendationReason] = []
        
        # Core status reasons
        reasons.append(RecommendationReason(
            code=f"ELIGIBILITY_STATUS_{eligibility.status.name}",
            description=f"Campaign eligibility evaluated as {eligibility.status.name}."
        ))
        
        reasons.append(RecommendationReason(
            code=f"WORTH_IT_RATING_{worth_it.overall_rating.name}",
            description=f"Campaign worth-it rating evaluated as {worth_it.overall_rating.name}."
        ))
        
        # Incorporate specific eligibility issues
        for issue in eligibility.issues:
            code = f"ELIGIBILITY_{issue.severity.name}_{issue.rule_name.upper().replace(' ', '_')}"
            reasons.append(RecommendationReason(
                code=code,
                description=issue.description
            ))
            
        # Incorporate specific worth-it findings
        for finding in worth_it.findings:
            prefix = "MISSING_INFO" if finding.is_missing_information else "WORTH_IT"
            code = f"{prefix}_{finding.rule_name.upper().replace(' ', '_')}"
            reasons.append(RecommendationReason(
                code=code,
                description=finding.description
            ))
            
        return RecommendationRationale(reasons=reasons)
