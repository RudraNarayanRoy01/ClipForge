from typing import Sequence

from src.reasoning.extraction.models import CampaignEntityDocument
from src.reasoning.eligibility.models import EligibilityAssessment
from .interfaces import IWorthItAssessmentEngine, IWorthItRule
from .models import WorthItAssessment, WorthItFinding, WorthItRating, AssessmentConfidence


class DefaultWorthItAssessmentEngine(IWorthItAssessmentEngine):
    """
    Default implementation of the Worth-It Assessment Engine.
    Coordinates independent rules to produce objective findings, and synthesizes 
    an overall rating and confidence score based strictly on those findings.
    """
    
    def __init__(self, rules: Sequence[IWorthItRule]):
        self._rules = rules
        
    def assess(
        self, 
        document: CampaignEntityDocument, 
        eligibility: EligibilityAssessment
    ) -> WorthItAssessment:
        
        all_findings = []
        
        for rule in self._rules:
            findings = rule.evaluate(document, eligibility)
            all_findings.extend(findings)
            
        confidence = self._determine_confidence(all_findings)
        rating = self._determine_rating(all_findings, eligibility)
        
        return WorthItAssessment(
            overall_rating=rating,
            confidence=confidence,
            findings=all_findings
        )
        
    def _determine_confidence(self, findings: list[WorthItFinding]) -> AssessmentConfidence:
        """
        Calculates confidence based on whether critical information is missing.
        """
        missing_info_count = sum(1 for f in findings if f.is_missing_information)
        
        if missing_info_count == 0:
            return AssessmentConfidence.HIGH
        elif missing_info_count == 1:
            return AssessmentConfidence.MEDIUM
        else:
            return AssessmentConfidence.LOW
            
    def _determine_rating(
        self, 
        findings: list[WorthItFinding], 
        eligibility: EligibilityAssessment
    ) -> WorthItRating:
        """
        Synthesizes the overall rating from the findings without external dependencies.
        """
        # If the campaign is fundamentally ineligible, it is rated POOR.
        if not eligibility.is_eligible:
            return WorthItRating.POOR
            
        observations = {f.observation for f in findings}
        
        has_reward = "Reward Present" in observations
        is_high_workload = "High Deliverable Count" in observations
        is_high_complexity = "High Complexity" in observations
        missing_actionable = "Missing Actionable Information" in observations
        
        if missing_actionable:
            return WorthItRating.UNKNOWN
            
        if has_reward:
            # Reward present: generally favorable, penalize for high workload/complexity
            if is_high_workload and is_high_complexity:
                return WorthItRating.FAIR
            elif is_high_workload or is_high_complexity:
                return WorthItRating.GOOD
            else:
                return WorthItRating.EXCELLENT
        else:
            # No reward: generally unfavorable, penalize further for workload/complexity
            if is_high_workload or is_high_complexity:
                return WorthItRating.POOR
            else:
                return WorthItRating.FAIR
