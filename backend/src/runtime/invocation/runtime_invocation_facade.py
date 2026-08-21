from typing import Sequence

from src.runtime.invocation.runtime_pipeline import RuntimePipeline
from src.runtime.execution.runtime_execution_boundary import RuntimeExecutionBoundary
from src.runtime.execution.execution_engine import ExecutionEngine
from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_context import PlanningContext
from src.runtime.core.execution_target import TargetDescription
from src.runtime.execution.execution_result import ExecutionResult, ExecutionOutcome
from src.runtime.execution.workload_normalizer import WorkloadNormalizationError
from src.runtime.execution.workload_normalization_extension import NormalizerResolutionError
from src.runtime.core.providers import RuntimeProviderRegistry


class RuntimeInvocationFacade:
    """
    Authoritative Runtime Invocation Bridge.
    
    Connects the decision completion boundary (RuntimePipeline) to the
    admission and execution boundaries (RuntimeExecutionBoundary, ExecutionEngine).
    
    It performs no target selection, policy evaluation, routing, or execution.
    It strictly orchestrates the flow of data across the established Runtime boundaries.
    """

    def __init__(
        self,
        pipeline: RuntimePipeline,
        boundary: RuntimeExecutionBoundary,
        engine: ExecutionEngine,
        provider_registry: RuntimeProviderRegistry
    ) -> None:
        self._pipeline = pipeline
        self._boundary = boundary
        self._engine = engine
        self._provider_registry = provider_registry

    def invoke(
        self,
        intent: ExecutionIntent,
        planning_context: PlanningContext
    ) -> ExecutionResult:
        """
        Orchestrate the transition from decision to execution.
        
        1. Query provider registry for available execution targets.
        2. Pass intent to RuntimePipeline to yield an ExecutionTarget.
        3. Pass target and intent to RuntimeExecutionBoundary to yield an ExecutionAdmission.
        4. Pass admission to ExecutionEngine to yield an ExecutionResult.
        """
        available_targets = [
            TargetDescription(
                target_id=reg.descriptor.identity.identifier,
                target_class=reg.descriptor.category.value,
                provider=reg.descriptor.identity.identifier,
            )
            for reg in self._provider_registry.enumerate_providers()
        ]

        target = self._pipeline.process(
            intent=intent,
            planning_context=planning_context,
            available_targets=available_targets
        )

        if target is None:
            return ExecutionResult(
                execution_target=None,
                outcome=ExecutionOutcome.REJECTED,
                error_message="No compatible execution target found by decision pipeline."
            )

        try:
            admission = self._boundary.execute(
                target=target,
                intent=intent
            )
        except (WorkloadNormalizationError, NormalizerResolutionError) as e:
            return ExecutionResult(
                execution_target=target,
                outcome=ExecutionOutcome.REJECTED,
                error_message=str(e)
            )

        result = self._engine.execute(
            admission=admission
        )

        return result
