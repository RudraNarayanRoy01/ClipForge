from backend.src.reasoning.recommendation.models import (
    RecommendationRequest,
    RecommendationInput,
    Recommendation
)
from backend.src.reasoning.recommendation.factory import IRecommendationContextFactory
from backend.src.reasoning.recommendation.engine import IRecommendationEngine
from backend.src.reasoning.recommendation.policy import IRecommendationPolicy
from backend.src.reasoning.recommendation.service.interfaces import IRecommendationService
from backend.src.reasoning.recommendation.service.exceptions import RecommendationServiceError


class DefaultRecommendationService(IRecommendationService):
    """
    Default implementation of the Recommendation Service orchestrator.
    It orchestrates the pipeline: context construction -> rule execution -> policy interpretation.
    It does not own any domain business logic itself.
    """

    def __init__(
        self,
        context_factory: IRecommendationContextFactory,
        engine: IRecommendationEngine,
        policy: IRecommendationPolicy
    ):
        self._context_factory = context_factory
        self._engine = engine
        self._policy = policy

    def generate_recommendation(
        self,
        request: RecommendationRequest,
        input_data: RecommendationInput
    ) -> Recommendation:
        """
        Orchestrates the pipeline and returns the finalized recommendation.
        """
        try:
            # 1. Build context using factory (unpacking input_data)
            context = self._context_factory.create_context(
                facts=input_data.facts,
                days_to_deadline=input_data.days_to_deadline,
                estimated_reward=input_data.estimated_reward,
                confidence_score=input_data.confidence_score,
                estimated_effort=input_data.estimated_effort,
                risk_score=input_data.risk_score,
                target_platform=input_data.target_platform,
                content_category=input_data.content_category
            )

            # 2. Execute engine
            result = self._engine.evaluate(request_id=request.id, context=context)

            # 3. Interpret result using policy
            decision = self._policy.interpret(result=result)

            # 4. Compose final Recommendation aggregate
            return Recommendation(
                request=request,
                context=context,
                result=result,
                decision=decision
            )

        except Exception as e:
            raise RecommendationServiceError(f"Recommendation generation failed: {str(e)}") from e
