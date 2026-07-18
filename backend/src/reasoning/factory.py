from src.reasoning.interfaces import ICampaignReasoningService
from src.reasoning.eligibility.interfaces import IEligibilityAssessmentEngine
from src.reasoning.worth_it.interfaces import IWorthItAssessmentEngine
from src.reasoning.recommendation.interfaces import IRecommendationSynthesisEngine
from src.reasoning.services.campaign_reasoning_service import DefaultCampaignReasoningService


class CampaignReasoningFactory:
    """
    Factory for instantiating the CampaignReasoningService.
    Serves as the canonical composition root for the Campaign Reasoning bounded context.
    Assembles the application service using its interface-based dependencies.
    """

    @staticmethod
    def create_service(
        eligibility_engine: IEligibilityAssessmentEngine,
        worth_it_engine: IWorthItAssessmentEngine,
        recommendation_engine: IRecommendationSynthesisEngine
    ) -> ICampaignReasoningService:
        """
        Assembles and returns a fully configured ICampaignReasoningService.
        """
        return DefaultCampaignReasoningService(
            eligibility_engine=eligibility_engine,
            worth_it_engine=worth_it_engine,
            recommendation_engine=recommendation_engine
        )
