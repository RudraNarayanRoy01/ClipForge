from typing import Sequence, Optional

from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_context import PlanningContext
from src.runtime.core.execution_target import ExecutionTarget, TargetDescription
from src.runtime.composition.runtime_pipeline_context import RuntimePipelineContext


class RuntimePipeline:
    """
    Authoritative Runtime Pipeline Invocation Boundary.
    
    Orchestrates the certified components (Planner -> Policy -> Router -> Selector)
    into a single deterministic pipeline without constructing dependencies, 
    executing work, or introducing speculative behavior.
    """

    def __init__(self, context: RuntimePipelineContext):
        """
        Constructor injects the pre-assembled composition graph.
        Does not construct any certified components.
        """
        self._context = context

    def process(
        self,
        intent: ExecutionIntent,
        planning_context: PlanningContext,
        available_targets: Sequence[TargetDescription]
    ) -> Optional[ExecutionTarget]:
        """
        Deterministically invoke the pipeline sequence to map an abstract intent 
        and context into a concrete execution target from the supplied catalog.
        
        Returns None if policy rejects, routing fails, or no target is compatible.
        """
        # 1. ExecutionPlanner answers WHAT abstract strategy fulfills the intent
        planning_result = self._context.execution_planner.plan(
            intent=intent,
            context=planning_context
        )

        # 2. PolicyEngine answers whether the abstract strategy is APPROVED
        policy_decision = self._context.policy_engine.evaluate(
            planning_result=planning_result,
            context=planning_context
        )

        # 3. RoutingEngine maps the policy decision into an abstract execution class
        # If policy rejected, routing engine returns is_routed=False
        route_decision = self._context.routing_engine.evaluate(
            policy_decision=policy_decision
        )

        # 4. TargetSelector maps the abstract route to a concrete target
        # If is_routed=False, selector naturally returns None
        # If no compatible target exists in the catalog, selector returns None
        execution_target = self._context.target_selector.select(
            route_decision=route_decision,
            available_targets=available_targets
        )

        return execution_target
