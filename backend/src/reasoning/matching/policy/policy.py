from typing import List

from src.reasoning.matching.models import MatchResult, PolicyDecision, MatchConfidence, PolicyRationale
from src.reasoning.matching.policy.interfaces import IMatchPolicy


class DefaultMatchPolicy(IMatchPolicy):
    """
    Default implementation of the Match Policy.
    Evaluates MatchResult to produce deterministic business decisions without modifying the result.
    Moves all confidence aggregation into the policy.
    """
    
    def evaluate(self, result: MatchResult) -> PolicyDecision:
        reasons: List[str] = []
        warnings: List[str] = []
        
        # 1. Evaluate Individual Rule Confidences to derive overall confidence
        overall_confidence = MatchConfidence.LOW
        
        if not result.matched_requirements:
            warnings.append("No matched requirements to evaluate confidence from.")
            # Fallback to engine's raw confidence if available, otherwise LOW
            if result.confidence:
                overall_confidence = result.confidence
            else:
                overall_confidence = MatchConfidence.LOW
        else:
            met_requirements = [req for req in result.matched_requirements if req.is_met]
            failed_requirements = [req for req in result.matched_requirements if not req.is_met]
            
            if failed_requirements:
                warnings.append(f"{len(failed_requirements)} requirements were not met.")
                overall_confidence = MatchConfidence.LOW
            else:
                confidences = [req.confidence for req in met_requirements if req.confidence is not None]
                if not confidences:
                    warnings.append("Requirements met but lack explicit confidence scores.")
                    overall_confidence = MatchConfidence.MEDIUM
                elif MatchConfidence.LOW in confidences:
                    overall_confidence = MatchConfidence.LOW
                elif MatchConfidence.HIGH in confidences:
                    overall_confidence = MatchConfidence.HIGH
                else:
                    overall_confidence = MatchConfidence.MEDIUM

        # 2. Determine Business Outcome (Acceptance/Rejection)
        # Business logic: A result is accepted if the engine marked it successful 
        # AND the policy determines the overall confidence is HIGH or MEDIUM.
        accepted = result.is_successful and overall_confidence in (MatchConfidence.HIGH, MatchConfidence.MEDIUM)
        
        if accepted:
            reasons.append("Result met business criteria for acceptance.")
        else:
            if not result.is_successful:
                reasons.append("Engine indicated result was not successful.")
            if overall_confidence == MatchConfidence.LOW:
                reasons.append("Overall confidence evaluated as LOW, rejecting match.")

        if result.reasoning:
            reasons.append(f"Engine context: {result.reasoning}")
            
        rationale = PolicyRationale(reasons=reasons, warnings=warnings)

        return PolicyDecision(
            accepted=accepted,
            overall_confidence=overall_confidence,
            rationale=rationale
        )

