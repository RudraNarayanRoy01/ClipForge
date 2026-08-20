from typing import Sequence

from src.runtime.invocation.runtime_pipeline import RuntimePipeline
from src.runtime.execution.runtime_execution_boundary import RuntimeExecutionBoundary
from src.runtime.execution.execution_engine import ExecutionEngine
from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_context import PlanningContext
from src.runtime.core.execution_target import TargetDescription
from src.runtime.execution.execution_result import ExecutionResult


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
        engine: ExecutionEngine
    ) -> None:
        self._pipeline = pipeline
        self._boundary = boundary
        self._engine = engine

    def invoke(
        self,
        intent: ExecutionIntent,
        planning_context: PlanningContext,
        available_targets: Sequence[TargetDescription]
    ) -> ExecutionResult:
        """
        Orchestrate the transition from decision to execution.
        
        1. Pass intent to RuntimePipeline to yield an ExecutionTarget.
        2. Pass target and intent to RuntimeExecutionBoundary to yield an ExecutionAdmission.
        3. Pass admission to ExecutionEngine to yield an ExecutionResult.
        """
        target = self._pipeline.process(
            intent=intent,
            planning_context=planning_context,
            available_targets=available_targets
        )

        if target is None:
            raise ValueError("No compatible execution target found by decision pipeline.")

        admission = self._boundary.execute(
            target=target,
            intent=intent
        )

        result = self._engine.execute(
            admission=admission
        )

        return result
