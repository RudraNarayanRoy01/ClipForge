from dataclasses import dataclass, field
from typing import Dict, Any, List

from .runtime_constraint_engine import ConstraintDecision


@dataclass(frozen=True)
class BudgetDecision:
    """
    Immutable canonical Budget Decision artifact.
    
    Represents the Runtime's architectural execution budget.
    Answers exactly one question: 'What execution budget is available?'
    
    It MUST NEVER contain:
    - routing decisions
    - scheduling
    - execution commands
    - provider selection
    - hardware decisions
    - optimization results
    - execution state
    - constraint definitions
    
    This artifact remains reusable across future Runtime decision layers
    (e.g., RuntimeRouting, RuntimeScheduler, RuntimeExecution)
    without being modified.
    """
    budget_identifier: str
    budget_status: str
    budget_rationale: str
    budget_assumptions: List[str] = field(default_factory=list)
    budget_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeBudgetPlanner:
    """
    The canonical Runtime Budget Planner subsystem.
    
    Responsibilities:
    - Consume immutable ConstraintDecision
    - Produce immutable BudgetDecision
    - Answer exactly one architectural question: 'What execution budget is available?'
    
    Must NEVER:
    - Answer 'What architectural constraints apply?' (RuntimeConstraintEngine)
    - Answer 'Where should it execute?' (Routing)
    - Answer 'When should it execute?' (Scheduler)
    - Answer 'Execute the workload.' (Execution)
    - Modify ConstraintDecision
    """

    def __init__(self) -> None:
        pass

    def evaluate(self, constraint_decision: ConstraintDecision) -> BudgetDecision:
        """
        Evaluate an immutable ConstraintDecision and produce an immutable BudgetDecision.
        """
        if not constraint_decision or constraint_decision.constraint_status != "ESTABLISHED":
            return BudgetDecision(
                budget_identifier="default-budget",
                budget_status="UNAVAILABLE",
                budget_rationale="Cannot establish budget for unestablished or missing ConstraintDecision.",
                budget_assumptions=["Constraints must be ESTABLISHED to evaluate budget."],
                budget_metadata={"evaluator": "RuntimeBudgetPlanner", "error": "Invalid input state"}
            )
            
        return BudgetDecision(
            budget_identifier="default-budget",
            budget_status="ESTABLISHED",
            budget_rationale="Architectural execution budget successfully established for ConstraintDecision.",
            budget_assumptions=[
                "Budget operates independently of constraint evaluation.",
                "Budget does not perform routing, scheduling, or execution decisions."
            ],
            budget_metadata={
                "evaluator": "RuntimeBudgetPlanner",
                "evaluated_constraint": constraint_decision.constraint_identifier
            }
        )
