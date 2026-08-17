from typing import Any, Dict, Tuple

from .intent import ExecutionIntent
from .planning_result import PlanningResult


class ExecutionPlanner:
    """
    Transforms an ExecutionIntent into a PlanningResult.

    This Planner establishes the authoritative boundary between WHAT work is requested
    (ExecutionIntent) and HOW the Runtime intends to execute it (PlanningResult).

    It answers "HOW does the Runtime intend to satisfy this requested work?" in the most
    abstract possible sense. It explicitly does not answer WHO, WHERE, WHEN, WHICH provider,
    WHICH hardware, or HOW to schedule or execute.
    """

    def plan(self, intent: ExecutionIntent) -> PlanningResult:
        """
        Produce a PlanningResult without modifying the input intent.

        For this foundational batch, the strategy is explicitly the deterministic neutral marker
        'default_planning_strategy', and requirements/constraints are intentionally empty.
        Rich planning logic is deferred to future batches to prevent coupling with
        infrastructure configuration at this layer.
        """
        # Preserves the exact object identity of intent.
        # Deterministic, neutral default strategy as repository lacks rich routing rules.
        strategy = "default_planning_strategy"

        # Empty declarative requirements as instructed by Batch 6B.4.2 specifications.
        requirements: Tuple[str, ...] = ()

        # Empty declarative constraints to prevent hidden configuration channels.
        constraints: Dict[str, Any] = {}

        return PlanningResult(
            intent=intent,
            strategy=strategy,
            requirements=requirements,
            constraints=constraints,
        )
