from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass(frozen=True)
class PlanningStrategy:
    """
    Immutable canonical Planning Strategy artifact.
    
    Represents the architectural planning philosophy used by RuntimePlanning.
    It MUST NEVER contain:
    - Executed commands
    - Scheduling information
    - Routing decisions
    - Provider selection
    - Policy decisions
    - Hardware preferences
    - Resource allocation
    """
    strategy_identifier: str
    strategy_name: str
    planning_philosophy: str
    planning_assumptions: List[str] = field(default_factory=list)
    planning_preferences: Dict[str, Any] = field(default_factory=dict)
    planning_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimePlanningStrategy:
    """
    The canonical Runtime Planning Strategy subsystem.
    
    Responsibilities:
    - Produce immutable PlanningStrategy
    - Answer exactly one architectural question: 'Which planning philosophy should guide RuntimePlanning?'
    
    Must NEVER:
    - Execute work
    - Answer 'Can it happen?' (Policy)
    - Answer 'When should it happen?' (Scheduler)
    - Answer 'Where should it happen?' (Routing)
    - Answer 'Execute it.' (Execution Engine)
    - Mutate RuntimeKnowledge
    - Perform provider or hardware selection
    """
    
    def __init__(self) -> None:
        pass
        
    def get_strategy(self) -> PlanningStrategy:
        """
        Generate and return the canonical immutable PlanningStrategy.
        """
        return PlanningStrategy(
            strategy_identifier="default-planning-strategy",
            strategy_name="Baseline Adaptive Planning",
            planning_philosophy="Maintain execution stability while monitoring variance.",
            planning_assumptions=["Assume baseline operation unless knowledge indicates otherwise."],
            planning_preferences={"prioritize_stability": True},
            planning_metadata={"version": "1.0", "generator": "RuntimePlanningStrategy"}
        )
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

    def plan(self, session_id: str, planning_strategy: PlanningStrategy, current_time: float) -> PlanningDecision:
        """
        Produce immutable PlanningDecision.
        Preserves architectural boundaries by only defining 'What should happen next?'.
        """
        if not session_id or session_id == "invalid":
            return PlanningDecision(
                session_id="invalid",
                planning_objective="No objective identified",
                planning_rationale="No valid session provided.",
                planning_confidence=0.0,
                planning_assumptions=["Invalid input state"],
                planning_metadata={"error": "No valid session.", "timestamp": current_time}
            )

        objective = "Continue standard execution"
        rationale = "Baseline operation planned."
        confidence = 0.5
        assumptions = list(planning_strategy.planning_assumptions)

        if "prioritize_stability" in planning_strategy.planning_preferences:
            assumptions.append("Stability prioritized by strategy.")

        return PlanningDecision(
            session_id=session_id,
            planning_objective=objective,
            planning_rationale=rationale,
            planning_confidence=confidence,
            planning_assumptions=assumptions,
            planning_metadata={"planned_by": "RuntimePlanning", "timestamp": current_time}
        )

