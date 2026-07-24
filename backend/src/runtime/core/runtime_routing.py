from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from .runtime_budget_planner import BudgetDecision


@dataclass(frozen=True)
class RoutingDecision:
    """
    Immutable canonical Routing Decision artifact.
    
    Represents the Runtime's architectural execution routing.
    Answers exactly one question: 'Where should this workload execute?'
    
    It MUST NEVER contain:
    - scheduling
    - execution commands
    - execution state
    - retry state
    - provider implementation
    - hardware implementation
    - optimization results
    - budget values
    
    This artifact remains immutable, deterministic, append-only, 
    provider independent, and hardware independent.
    """
    routing_identifier: str
    routing_status: str
    primary_route_identifier: str
    fallback_route_identifier: Optional[str] = None
    routing_rationale: str = ""
    routing_assumptions: List[str] = field(default_factory=list)
    routing_metadata: Dict[str, Any] = field(default_factory=dict)


class RuntimeRouting:
    """
    The canonical Runtime Routing subsystem.
    
    Responsibilities:
    - Consume immutable BudgetDecision
    - Produce immutable RoutingDecision
    - Answer exactly one architectural question: 'Where should this workload execute?'
    
    Must NEVER:
    - Answer 'What execution budget is available?' (RuntimeBudgetPlanner)
    - Answer 'When should it execute?' (RuntimeScheduler)
    - Answer 'Execute the workload.' (RuntimeExecution)
    - Answer 'Retry execution.' (RuntimeExecution)
    - Modify BudgetDecision
    """

    def __init__(self) -> None:
        pass

    def evaluate(self, budget_decision: BudgetDecision) -> RoutingDecision:
        """
        Evaluate an immutable BudgetDecision and produce an immutable RoutingDecision.
        """
        if not budget_decision or budget_decision.budget_status != "ESTABLISHED":
            return RoutingDecision(
                routing_identifier="default-routing",
                routing_status="UNAVAILABLE",
                primary_route_identifier="NONE",
                fallback_route_identifier="NONE",
                routing_rationale="Cannot establish routing for unestablished or missing BudgetDecision.",
                routing_assumptions=["Budget must be ESTABLISHED to evaluate routing."],
                routing_metadata={"evaluator": "RuntimeRouting", "error": "Invalid input state"}
            )
            
        return RoutingDecision(
            routing_identifier="default-routing",
            routing_status="ESTABLISHED",
            primary_route_identifier="default-primary-route",
            fallback_route_identifier="default-fallback-route",
            routing_rationale="Architectural execution routing successfully established for BudgetDecision.",
            routing_assumptions=[
                "Routing operates independently of budget evaluation.",
                "Routing does not perform scheduling, execution, or provider selection."
            ],
            routing_metadata={
                "evaluator": "RuntimeRouting",
                "evaluated_budget": budget_decision.budget_identifier
            }
        )
