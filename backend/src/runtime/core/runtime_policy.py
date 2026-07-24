from dataclasses import dataclass, field
from typing import Dict, Any, List

from .runtime_planning import PlanningDecision


@dataclass(frozen=True)
class PolicyDecision:
    """
    Immutable canonical Policy Decision artifact.
    
    Represents the Runtime's architectural approval decision.
    Answers exactly one question: 'Is this PlanningDecision permitted?'
    
    It MUST NEVER contain:
    - execution commands
    - scheduling
    - routing
    - constraint results
    - budget values
    - provider selection
    - hardware decisions
    - resource allocation
    """
    policy_identifier: str
    approval_status: str
    evaluation_rationale: str
    evaluation_assumptions: List[str] = field(default_factory=list)
    policy_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimePolicy:
    """
    The canonical Runtime Policy subsystem.
    
    Responsibilities:
    - Consume immutable PlanningDecision
    - Produce immutable PolicyDecision
    - Answer exactly one architectural question: 'Is this PlanningDecision permitted?'
    
    Must NEVER:
    - Answer 'What should happen next?' (Planning)
    - Answer 'How should planning be approached?' (PlanningStrategy)
    - Answer 'What constraints apply?' (ConstraintEngine)
    - Answer 'Can we afford this?' (BudgetPlanner)
    - Answer 'Where should it execute?' (Routing)
    - Answer 'When should it execute?' (Scheduler)
    - Answer 'Execute the workload.' (Execution)
    - Modify PlanningDecision
    """

    def __init__(self) -> None:
        pass

    def evaluate(self, planning_decision: PlanningDecision) -> PolicyDecision:
        """
        Evaluate an immutable PlanningDecision and produce an immutable PolicyDecision.
        """
        if not planning_decision or planning_decision.session_id == "invalid":
            return PolicyDecision(
                policy_identifier="default-policy",
                approval_status="DENIED",
                evaluation_rationale="Invalid or missing PlanningDecision.",
                evaluation_assumptions=["Invalid input state"],
                policy_metadata={"evaluator": "RuntimePolicy", "error": "Invalid input"}
            )
            
        return PolicyDecision(
            policy_identifier="default-policy",
            approval_status="APPROVED",
            evaluation_rationale="PlanningDecision architecturally permitted.",
            evaluation_assumptions=[
                "Policy evaluation operates independently of execution logic.",
                "Policy assumes PlanningDecision is complete and untampered."
            ],
            policy_metadata={
                "evaluator": "RuntimePolicy",
                "evaluated_session": planning_decision.session_id
            }
        )
