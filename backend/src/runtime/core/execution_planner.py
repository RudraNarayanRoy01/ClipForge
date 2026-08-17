from typing import Any, Dict, Tuple

from .intent import ExecutionIntent
from .planning_context import PlanningContext
from .planning_result import PlanningResult


class ExecutionPlanner:
    """
    Transforms an ExecutionIntent into a PlanningResult based on a PlanningContext.

    This Planner establishes the authoritative boundary between WHAT work is requested
    (ExecutionIntent) and HOW the Runtime intends to execute it (PlanningResult),
    influenced by declarative planning preferences (PlanningContext).

    It answers "HOW does the Runtime intend to satisfy this requested work?" in the most
    abstract possible sense. It explicitly does not answer WHO, WHERE, WHEN, WHICH provider,
    WHICH hardware, or HOW to schedule or execute.
    """

    def plan(self, intent: ExecutionIntent, context: PlanningContext) -> PlanningResult:
        """
        Produce a PlanningResult without modifying the input intent or context.

        Strategy is selected deterministically based on a strict precedence of
        PlanningContext preferences: Quality > Latency > Cost > Locality.
        
        Requirements and constraints are intentionally empty, deferring richer 
        constraint materialization to prevent hidden infrastructure coupling.
        """
        if context.quality_preference == "high":
            strategy = "quality_first_planning"
        elif context.latency_preference == "low":
            strategy = "latency_first_planning"
        elif context.cost_preference == "low":
            strategy = "cost_aware_planning"
        elif context.locality_preference == "local":
            strategy = "locality_preferred_planning"
        else:
            strategy = "balanced_planning"

        # Requirements remain empty as no reliable provider-neutral requirements
        # can be safely derived without inventing domain/infrastructure semantics.
        requirements: Tuple[str, ...] = ()

        # Constraints remain empty as a safe default (Option B).
        # PlanningContext.constraints are NOT converted into requirements or constraints.
        constraints: Dict[str, Any] = {}

        return PlanningResult(
            intent=intent,
            strategy=strategy,
            requirements=requirements,
            constraints=constraints,
        )
