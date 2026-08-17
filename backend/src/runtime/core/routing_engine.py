from .policy_decision import PolicyDecision
from .route_decision import RouteDecision


class RoutingEngine:
    """
    Establishes the clean abstract routing boundary immediately downstream 
    of the Policy layer.

    It determines the abstract execution class based on the PolicyDecision.
    It explicitly does NOT perform provider selection, hardware discovery,
    or workload scheduling.
    """

    def evaluate(self, policy_decision: PolicyDecision) -> RouteDecision:
        """
        Produce a RouteDecision deterministically based on the PolicyDecision.
        """
        if not policy_decision.is_approved:
            return RouteDecision(
                policy_decision=policy_decision,
                execution_class="none",
                is_routed=False,
                fallback_allowed=False
            )

        # Map policy mode to an abstract execution class
        mode = policy_decision.policy_mode
        if mode == "locality_preferred":
            execution_class = "abstract_local"
        elif mode == "cost_constrained":
            execution_class = "abstract_remote"
        else:
            execution_class = "abstract_balanced"

        return RouteDecision(
            policy_decision=policy_decision,
            execution_class=execution_class,
            is_routed=True,
            fallback_allowed=policy_decision.fallback_allowed
        )
