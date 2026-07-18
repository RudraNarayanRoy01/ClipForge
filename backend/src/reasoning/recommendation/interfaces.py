from abc import ABC, abstractmethod

from src.reasoning.extraction.models import CampaignEntityDocument
from src.reasoning.eligibility.models import EligibilityAssessment
from src.reasoning.worth_it.models import WorthItAssessment
from src.reasoning.recommendation.models import Recommendation


class IRecommendationSynthesisEngine(ABC):
    """
    Synthesizes existing assessments into a deterministic final recommendation.
    Does not perform new reasoning or business analysis.
    """
    
    @abstractmethod
    def synthesize(
        self,
        document: CampaignEntityDocument,
        eligibility: EligibilityAssessment,
        worth_it: WorthItAssessment
    ) -> Recommendation:
        """
        Combines the extracted document and assessments into a final recommendation.
        """
        pass
