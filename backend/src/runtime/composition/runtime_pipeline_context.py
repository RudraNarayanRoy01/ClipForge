from dataclasses import dataclass
from src.runtime.core.execution_planner import ExecutionPlanner
from src.runtime.core.policy_engine import PolicyEngine
from src.runtime.core.routing_engine import RoutingEngine
from src.runtime.core.target_selector import TargetSelector

@dataclass(frozen=True)
class RuntimePipelineContext:
    """
    Represents the assembled Runtime dependency graph for the certified pipeline.
    
    This is a passive dependency container representing the Runtime's object graph.
    It does NOT execute work, schedule, or load models.
    """
    execution_planner: ExecutionPlanner
    policy_engine: PolicyEngine
    routing_engine: RoutingEngine
    target_selector: TargetSelector
