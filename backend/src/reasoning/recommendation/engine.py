from src.reasoning.extraction.models import CampaignEntityDocument
from src.reasoning.eligibility.models import EligibilityAssessment
from src.reasoning.worth_it.models import WorthItAssessment
from src.reasoning.recommendation.models import Recommendation
from src.reasoning.recommendation.interfaces import IRecommendationSynthesisEngine
from src.reasoning.recommendation.policy import RecommendationPolicy


class DefaultRecommendationSynthesisEngine(IRecommendationSynthesisEngine):
    """
    Default implementation of the recommendation synthesis engine.
    Delegates deterministic decision making to the RecommendationPolicy.
    """

    def __init__(self, policy: RecommendationPolicy = None):
        """
        Initializes the engine with a recommendation policy.
        """
        self._policy = policy or RecommendationPolicy()

    def synthesize(
        self,
        document: CampaignEntityDocument,
        eligibility: EligibilityAssessment,
        worth_it: WorthItAssessment
    ) -> Recommendation:
        """
        Synthesizes the prior assessments into a final recommendation.
        The entity document is accepted for interface consistency and potential 
        traceability, but is not used to evaluate business rules.
        """
        return self._policy.synthesize(
            eligibility=eligibility,
            worth_it=worth_it
        )
