from dataclasses import dataclass, field
from typing import Dict, Any, List

from .runtime_learning import RuntimeKnowledge


@dataclass(frozen=True)
class PlanningDecision:
    """
    Immutable canonical Planning Decision artifact.
    
    Represents the Runtime's recommended future course of action based on RuntimeKnowledge.
    It MUST NEVER contain:
    - Executed actions
    - Runtime mutations
    - Scheduling decisions
    - Resource allocations
    - Provider selections
    - Policy decisions
    - Hardware decisions
    """
    session_id: str
    planning_objective: str
    planning_rationale: str
    planning_confidence: float = 0.0
    planning_assumptions: List[str] = field(default_factory=list)
    planning_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimePlanning:
    """
    The canonical Runtime Planning subsystem.
    
    Responsibilities:
    - Consume immutable RuntimeKnowledge
    - Transform accumulated Runtime knowledge into a future execution intention
    - Produce immutable PlanningDecision
    - Answer exactly one architectural question: 'What should happen next?'
    - Preserve Runtime architectural boundaries
    - Remain deterministic
    - Remain provider independent
    - Remain hardware independent
    
    Must NEVER:
    - Execute work
    - Answer 'Can it happen?' (Policy)
    - Answer 'When should it happen?' (Scheduler)
    - Answer 'Where should it happen?' (Routing)
    - Answer 'Execute it.' (Execution Engine)
    - Modify RuntimeKnowledge or any other artifact
    - Perform provider selection
    - Perform hardware selection
    - Allocate resources
    - Embed RuntimeKnowledge in PlanningDecision
    """

    def __init__(self) -> None:
        pass

    def plan(self, runtime_knowledge: RuntimeKnowledge, current_time: float) -> PlanningDecision:
        """
        Consume immutable RuntimeKnowledge and produce immutable PlanningDecision.
        Preserves architectural boundaries by only defining 'What should happen next?'.
        """
        if not runtime_knowledge or runtime_knowledge.session_id == "invalid":
            return PlanningDecision(
                session_id="invalid",
                planning_objective="No objective identified",
                planning_rationale="No valid runtime knowledge provided.",
                planning_confidence=0.0,
                planning_assumptions=["Invalid input state"],
                planning_metadata={"error": "No valid runtime knowledge provided.", "timestamp": current_time}
            )

        objective = "Continue standard execution"
        rationale = "Runtime knowledge indicates baseline operation."
        confidence = runtime_knowledge.learning_confidence
        assumptions = []

        if runtime_knowledge.knowledge_classifications:
            if "STABLE" in runtime_knowledge.knowledge_classifications:
                objective = "Apply stable optimization pattern"
                rationale = "Critical failure pattern identified in knowledge."
                assumptions.append("Failure conditions may reoccur.")
            elif "EMERGING" in runtime_knowledge.knowledge_classifications:
                objective = "Monitor for performance variance"
                rationale = "Emerging patterns indicate performance fluctuation."
                assumptions.append("Variance may persist.")

        if runtime_knowledge.learned_patterns:
            assumptions.extend([f"Observed: {p}" for p in runtime_knowledge.learned_patterns])

        return PlanningDecision(
            session_id=runtime_knowledge.session_id,
            planning_objective=objective,
            planning_rationale=rationale,
            planning_confidence=confidence,
            planning_assumptions=assumptions,
            planning_metadata={"planned_by": "RuntimePlanning", "timestamp": current_time}
        )
