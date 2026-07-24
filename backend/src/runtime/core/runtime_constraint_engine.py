from dataclasses import dataclass, field
from typing import Dict, Any, List

from .runtime_policy import PolicyDecision


@dataclass(frozen=True)
class ConstraintDecision:
    """
    Immutable canonical Constraint Decision artifact.
    
    Represents the Runtime's architectural execution boundaries.
    Answers exactly one question: 'What architectural constraints apply?'
    
    It MUST NEVER contain:
    - budget values
    - routing decisions
    - scheduling
    - execution commands
    - provider selection
    - hardware decisions
    - optimization results
    - execution state
    
    This artifact remains reusable across future Runtime decision layers
    (e.g., RuntimeBudgetPlanner, RuntimeRouting, RuntimeScheduler, RuntimeExecution)
    without being modified.
    """
    constraint_identifier: str
    constraint_status: str
    constraint_rationale: str
    constraint_assumptions: List[str] = field(default_factory=list)
    constraint_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeConstraintEngine:
    """
    The canonical Runtime Constraint Engine subsystem.
    
    Responsibilities:
    - Consume immutable PolicyDecision
    - Produce immutable ConstraintDecision
    - Answer exactly one architectural question: 'What architectural constraints apply?'
    
    Must NEVER:
    - Answer 'Is this plan permitted?' (RuntimePolicy)
    - Answer 'Can we afford this?' (BudgetPlanner)
    - Answer 'Where should it execute?' (Routing)
    - Answer 'When should it execute?' (Scheduler)
    - Answer 'Execute the workload.' (Execution)
    - Modify PolicyDecision
    """

    def __init__(self) -> None:
        pass

    def evaluate(self, policy_decision: PolicyDecision) -> ConstraintDecision:
        """
        Evaluate an immutable PolicyDecision and produce an immutable ConstraintDecision.
        """
        if not policy_decision or policy_decision.approval_status != "APPROVED":
            return ConstraintDecision(
                constraint_identifier="default-constraint",
                constraint_status="UNSATISFIABLE",
                constraint_rationale="Cannot establish constraints for unapproved or missing PolicyDecision.",
                constraint_assumptions=["Policy must be APPROVED to evaluate constraints."],
                constraint_metadata={"evaluator": "RuntimeConstraintEngine", "error": "Invalid input state"}
            )
            
        return ConstraintDecision(
            constraint_identifier="default-constraint",
            constraint_status="ESTABLISHED",
            constraint_rationale="Architectural constraints successfully established for PolicyDecision.",
            constraint_assumptions=[
                "Constraints operate independently of policy evaluation.",
                "Constraints do not perform budget, routing, or scheduling decisions."
            ],
            constraint_metadata={
                "evaluator": "RuntimeConstraintEngine",
                "evaluated_policy": policy_decision.policy_identifier
            }
        )
