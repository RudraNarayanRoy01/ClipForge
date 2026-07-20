import logging
import uuid

from src.reasoning.execution.composer.interfaces import IExecutionComposer
from src.reasoning.execution.models import ExecutionInput, ExecutionPlan
from src.reasoning.execution.planner.interfaces import IExecutionPlanner
from src.reasoning.execution.strategy.interfaces import IExecutionStrategy
from src.reasoning.execution.validation.interfaces import IExecutionValidation
from .interfaces import IExecutionService

logger = logging.getLogger(__name__)


class DefaultExecutionService(IExecutionService):
    """
    Deterministic implementation of the Execution Service.
    Orchestrates the pipeline without containing any business reasoning.
    """

    def __init__(
        self,
        planner: IExecutionPlanner,
        strategy: IExecutionStrategy,
        validation: IExecutionValidation,
        composer: IExecutionComposer,
    ):
        self._planner = planner
        self._strategy = strategy
        self._validation = validation
        self._composer = composer

    def generate_execution_plan(
        self,
        execution_input: ExecutionInput,
        plan_id: uuid.UUID,
    ) -> ExecutionPlan:
        """
        Orchestrates Planner, Strategy, Validation, and Composer sequentially.
        Produces deterministic output without altering upstream domain state.
        """
        logger.info(f"Starting execution plan generation for plan {plan_id}")

        # 1. Planner
        # The planner purely generates a draft of the segments.
        draft = self._planner.create_execution_draft(execution_input)

        # 2. Strategy
        # The strategy engine establishes editorial intent based on the draft.
        strategy_result = self._strategy.generate_strategy(draft)

        # 3. Validation
        # Validates structural consistency and compatibility, returning issues/warnings.
        validation_result = self._validation.validate_execution(
            draft=draft,
            strategy=strategy_result
        )

        # 4. Composer
        # Composes the final ExecutionPlan aggregate using immutable components.
        plan = self._composer.compose_execution_plan(
            plan_id=plan_id,
            draft=draft,
            strategy=strategy_result,
            validation=validation_result
        )

        logger.info(f"Successfully generated execution plan {plan_id}")
        return plan
