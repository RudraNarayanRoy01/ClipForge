from datetime import datetime, timezone
from dataclasses import replace

from src.reasoning.interfaces import ICampaignReasoningService
from src.reasoning.eligibility.interfaces import IEligibilityAssessmentEngine
from src.reasoning.worth_it.interfaces import IWorthItAssessmentEngine
from src.reasoning.recommendation.interfaces import IRecommendationSynthesisEngine
from src.reasoning.domain import (
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
        eligibility_engine: IEligibilityAssessmentEngine,
        worth_it_engine: IWorthItAssessmentEngine,
        recommendation_engine: IRecommendationSynthesisEngine
    ):
        self._eligibility_engine = eligibility_engine
        self._worth_it_engine = worth_it_engine
        self._recommendation_engine = recommendation_engine

    def evaluate_campaign(self, context: EvaluationContext) -> CampaignEvaluation:
        # Record the start of evaluation
        metadata_start = EvaluationMetadata(reasoning_version="2.0")

        try:
            # 1. Eligibility
            eligibility = self._eligibility_engine.assess(context.document)

            # 2. Worth-It
            worth_it = self._worth_it_engine.assess(context.document, eligibility)

            # 3. Recommendation
            recommendation = self._recommendation_engine.synthesize(
                document=context.document,
                eligibility=eligibility,
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
                worth_it=worth_it,
                recommendation=recommendation
            )
        except Exception:
            # The orchestrator owns exception propagation.
            # We allow the exception to bubble up to the caller without swallowing it.
            raise
