from .planning_context import PlanningContext
from .planning_result import PlanningResult
from .policy_decision import PolicyDecision


class PolicyEngine:
    """
    Evaluates a PlanningResult against a PlanningContext to produce a
    deterministic PolicyDecision.

    This Engine establishes the authoritative boundary between HOW work is planned
    and IS THAT HOW ACCEPTABLE. It explicitly does not select providers,
    hardware, or schedules.
    """

    def evaluate(
        self,
        planning_result: PlanningResult,
        context: PlanningContext,
    ) -> PolicyDecision:
        """
        Produce a PolicyDecision deterministically based on the PlanningResult
        and PlanningContext without modifying the inputs.
        """
        # Baseline deterministic approval for structurally valid inputs
        is_approved = True
        
        # Baseline deterministic fallback allowed
        fallback_allowed = True

        # Deterministic policy mode mapping based on the planning strategy
        strategy = planning_result.strategy
        if strategy == "quality_first_planning":
            policy_mode = "quality_protected"
        elif strategy == "latency_first_planning":
            policy_mode = "latency_protected"
        elif strategy == "cost_aware_planning":
            policy_mode = "cost_constrained"
        elif strategy == "locality_preferred_planning":
            policy_mode = "locality_preferred"
        else:
            policy_mode = "balanced"

        # Pass-through abstract constraints
        constraints = tuple(context.constraints)

        return PolicyDecision(
            planning_result=planning_result,
            is_approved=is_approved,
            policy_mode=policy_mode,
            fallback_allowed=fallback_allowed,
            constraints=constraints,
        )
