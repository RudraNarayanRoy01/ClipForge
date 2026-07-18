from typing import List, Protocol

from src.reasoning.extraction.models import CampaignEntityDocument
from src.reasoning.eligibility.models import EligibilityAssessment
from .models import WorthItAssessment, WorthItFinding


class IWorthItRule(Protocol):
    """
    Protocol for a single focused worth-it rule.
    Each rule produces objective observations (findings) without making judgments.
    """
    
    def evaluate(
        self, 
        document: CampaignEntityDocument, 
        eligibility: EligibilityAssessment
    ) -> List[WorthItFinding]:
        """
        Evaluates the given document and eligibility and returns a list of objective findings.
        """
        ...


class IWorthItAssessmentEngine(Protocol):
    """
    Protocol for the engine that evaluates the objective economic and 
    operational attractiveness of a campaign.
    """

    def assess(
        self, 
        document: CampaignEntityDocument, 
        eligibility: EligibilityAssessment
    ) -> WorthItAssessment:
        """
        Assess the inputs and return an immutable WorthItAssessment.
        """
        ...
