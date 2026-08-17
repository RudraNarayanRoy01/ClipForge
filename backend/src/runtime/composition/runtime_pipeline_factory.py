from src.runtime.core.execution_planner import ExecutionPlanner
from src.runtime.core.policy_engine import PolicyEngine
from src.runtime.core.routing_engine import RoutingEngine
from src.runtime.core.target_selector import TargetSelector
from .runtime_pipeline_context import RuntimePipelineContext

class RuntimePipelineFactory:
    """
    The canonical Runtime Composition Root for the certified pipeline.
    
    Assembles the Runtime dependency graph without executing logic.
    """
    
    @classmethod
    def create(cls) -> RuntimePipelineContext:
        """
        Constructs the deterministic Runtime dependency graph.
        """
        # Ensure single instances of pipeline components
        execution_planner = ExecutionPlanner()
        policy_engine = PolicyEngine()
        routing_engine = RoutingEngine()
        target_selector = TargetSelector()
        
        return RuntimePipelineContext(
            execution_planner=execution_planner,
            policy_engine=policy_engine,
            routing_engine=routing_engine,
            target_selector=target_selector
        )
