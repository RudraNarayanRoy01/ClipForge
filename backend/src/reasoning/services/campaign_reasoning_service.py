from datetime import datetime, timezone
from dataclasses import replace

from src.reasoning.interfaces import (
    ICampaignReasoningService,
    IEligibilityEngine,
    ICompatibilityEngine,
    ISuitabilityEngine,
    IRiskEngine,
    IWorthItEngine,
    IRecommendationEngine
)
from src.reasoning.domain.models import (
    EvaluationContext,
    CampaignEvaluation,
    EvaluationId,
    EvaluationStatus,
    EvaluationMetadata
)


class DefaultCampaignReasoningService(ICampaignReasoningService):
    """
    Default implementation of ICampaignReasoningService.
    Orchestrates the campaign evaluation pipeline by coordinating various reasoning engines.
    """

    def __init__(
        self,
        eligibility_engine: IEligibilityEngine,
        compatibility_engine: ICompatibilityEngine,
        suitability_engine: ISuitabilityEngine,
        risk_engine: IRiskEngine,
        worth_it_engine: IWorthItEngine,
        recommendation_engine: IRecommendationEngine
    ):
        self._eligibility_engine = eligibility_engine
        self._compatibility_engine = compatibility_engine
        self._suitability_engine = suitability_engine
        self._risk_engine = risk_engine
        self._worth_it_engine = worth_it_engine
        self._recommendation_engine = recommendation_engine

    async def evaluate_campaign(self, context: EvaluationContext) -> CampaignEvaluation:
        # Record the start of evaluation
        metadata_start = EvaluationMetadata(reasoning_version="2.0")

        try:
            # 1. Eligibility
            eligibility = await self._eligibility_engine.evaluate(context)

            # 2. Compatibility
            compatibility = await self._compatibility_engine.evaluate(context)

            # 3. Suitability
            suitability = await self._suitability_engine.evaluate(context)

            # 4. Risk
            risk = await self._risk_engine.assess(context)

            # 5. Worth-It
            worth_it = await self._worth_it_engine.evaluate(context)

            # 6. Recommendation
            recommendation = await self._recommendation_engine.generate_recommendation(
                context=context,
                eligibility=eligibility,
                compatibility=compatibility,
                suitability=suitability,
                risk=risk,
                worth_it=worth_it
            )

            # Assemble the final aggregate with completed status and timestamp
            metadata_completed = replace(
                metadata_start,
                completed_at=datetime.now(timezone.utc)
            )

            return CampaignEvaluation(
                id=EvaluationId(),
                status=EvaluationStatus.COMPLETED,
                context=context,
                metadata=metadata_completed,
                eligibility=eligibility,
                compatibility=compatibility,
                suitability=suitability,
                risk=risk,
                worth_it=worth_it,
                recommendation=recommendation
            )
        except Exception:
            # The orchestrator owns exception propagation.
            # We allow the exception to bubble up to the caller without swallowing it.
            raise
