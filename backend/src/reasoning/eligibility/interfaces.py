from typing import List, Protocol

from src.reasoning.extraction.models import CampaignEntityDocument
from .models import EligibilityAssessment, EligibilityIssue


class IEligibilityRule(Protocol):
    """
    Protocol for a single focused eligibility rule.
    Each rule assesses one specific aspect of the document deterministically.
    """
    
    def evaluate(self, document: CampaignEntityDocument) -> List[EligibilityIssue]:
        """
        Evaluates the given document and returns a list of discovered issues.
        Returns an empty list if no issues are found.
        """
        ...


class IEligibilityAssessmentEngine(Protocol):
    """
    Protocol for the engine that determines if a campaign is eligible.
    """

    def assess(self, document: CampaignEntityDocument) -> EligibilityAssessment:
        """
        Assess the document and return an immutable EligibilityAssessment.
        """
        ...
