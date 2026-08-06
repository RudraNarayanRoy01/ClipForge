from types import MappingProxyType
from typing import Any

from .runtime_execution_composition_statistics import RuntimeExecutionCompositionStatistics
from .runtime_execution_identity import RuntimeExecutionIdentity
from .runtime_execution_graph import RuntimeExecutionGraph
from .runtime_execution_plan import RuntimeExecutionPlan
from .runtime_execution_context import RuntimeExecutionContext

class ExecutionCompositionStatisticsBuilder:
    """
    Performs ONLY structural construction.
    
    NEVER performs:
    - execution
    - lifecycle
    - scheduling
    - provider loading
    - telemetry
    - monitoring
    - optimization
    - planning
    """
    @staticmethod
    def build(
        execution_identity: RuntimeExecutionIdentity,
        execution_graph: RuntimeExecutionGraph,
        execution_plan: RuntimeExecutionPlan,
        execution_context: RuntimeExecutionContext,
        identity_lookup: MappingProxyType[str, RuntimeExecutionIdentity],
        graph_lookup: MappingProxyType[str, RuntimeExecutionGraph],
        plan_lookup: MappingProxyType[str, RuntimeExecutionPlan],
        context_lookup: MappingProxyType[str, RuntimeExecutionContext],
        descriptor_lookup: MappingProxyType[str, Any],
        composition_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionCompositionStatistics:
        return RuntimeExecutionCompositionStatistics(
            identity_count=1 if execution_identity else 0,
            graph_count=1 if execution_graph else 0,
            plan_count=1 if execution_plan else 0,
            context_count=1 if execution_context else 0,
            identity_lookup_count=len(identity_lookup),
            graph_lookup_count=len(graph_lookup),
            plan_lookup_count=len(plan_lookup),
            context_lookup_count=len(context_lookup),
            descriptor_lookup_count=len(descriptor_lookup),
            composition_lookup_count=len(composition_lookup)
        )
