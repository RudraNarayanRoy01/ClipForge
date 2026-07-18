from src.reasoning.interfaces import (
    ICampaignReasoningService,
    IEligibilityEngine,
    ICompatibilityEngine,
    ISuitabilityEngine,
    IRiskEngine,
    IWorthItEngine,
    IRecommendationEngine
)
from src.reasoning.services.campaign_reasoning_service import DefaultCampaignReasoningService


class CampaignReasoningFactory:
    """
    Factory for instantiating the CampaignReasoningService.
    Serves as the canonical composition root for the Campaign Reasoning bounded context.
    Assembles the application service using its interface-based dependencies.
    """

    @staticmethod
    def create_service(
        eligibility_engine: IEligibilityEngine,
        compatibility_engine: ICompatibilityEngine,
        suitability_engine: ISuitabilityEngine,
        risk_engine: IRiskEngine,
        worth_it_engine: IWorthItEngine,
        recommendation_engine: IRecommendationEngine
    ) -> ICampaignReasoningService:
        """
        Assembles and returns a fully configured ICampaignReasoningService.
        """
        return DefaultCampaignReasoningService(
            eligibility_engine=eligibility_engine,
            compatibility_engine=compatibility_engine,
            suitability_engine=suitability_engine,
            risk_engine=risk_engine,
            worth_it_engine=worth_it_engine,
            recommendation_engine=recommendation_engine
        )
