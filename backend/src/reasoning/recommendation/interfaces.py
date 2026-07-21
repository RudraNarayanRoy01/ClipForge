from typing import Protocol

from src.reasoning.extraction.models import CampaignEntityDocument
from src.reasoning.eligibility.models import EligibilityAssessment
from src.reasoning.worth_it.models import WorthItAssessment
from src.reasoning.recommendation.models import Recommendation

class IRecommendationSynthesisEngine(Protocol):
    """
    Protocol for the engine that synthesizes the final Recommendation 
    by evaluating the document against eligibility and worth-it assessments.
    """
    
    def synthesize(
        self,
        document: CampaignEntityDocument,
        eligibility: EligibilityAssessment,
        worth_it: WorthItAssessment
    ) -> Recommendation:
        """
        Synthesizes and returns an immutable Recommendation aggregate.
        """
        ...
