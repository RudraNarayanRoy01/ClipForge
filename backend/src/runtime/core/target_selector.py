from typing import Sequence, Optional

from .route_decision import RouteDecision
from .execution_target import ExecutionTarget, TargetDescription


class TargetSelector:
    """
    Authoritative Runtime-level Concrete Execution Target Selection boundary.
    
    Responsible for resolving an accepted abstract RouteDecision into a concrete
    ExecutionTarget description from an explicitly available set of targets.
    """

    def select(
        self,
        route_decision: RouteDecision,
        available_targets: Sequence[TargetDescription]
    ) -> Optional[ExecutionTarget]:
        """
        Select a concrete execution target for the given routing decision.
        
        Must remain deterministic, payload-opaque, and purely descriptive.
        """
        # Respect Policy Rejection Rule
        if not route_decision.is_routed:
            return None

        # Abstract Class Matching
        # abstract_local -> local, abstract_remote -> remote, etc.
        expected_class = route_decision.execution_class
        if expected_class.startswith("abstract_"):
            expected_class = expected_class.replace("abstract_", "")

        # Find first eligible target deterministically
        for target in available_targets:
            if target.target_class == expected_class:
                return self._create_execution_target(route_decision, target)

        # Fallback semantics are explicitly removed from arbitrary selection.
        # fallback_allowed means fallback is permitted by policy, but it does NOT
        # establish compatibility with arbitrary targets. In the absence of an
        # explicit compatible fallback taxonomy, we return None if no exact match exists.

        return None

    def _create_execution_target(
        self,
        route_decision: RouteDecision,
        target: TargetDescription
    ) -> ExecutionTarget:
        return ExecutionTarget(
            route_decision=route_decision,
            target_id=target.target_id,
            target_class=target.target_class,
            provider=target.provider,
            model=target.model,
            compute_class=target.compute_class
        )
