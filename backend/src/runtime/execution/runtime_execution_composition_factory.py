from typing import Dict, Set, Optional, Any

from .runtime_execution_composition import RuntimeExecutionComposition
from .execution_composition_factory import ExecutionCompositionFactory
from .runtime_execution_composition_validator import RuntimeExecutionCompositionValidator
from .runtime_execution_identity import RuntimeExecutionIdentity
from .runtime_execution_graph import RuntimeExecutionGraph
from .runtime_execution_plan import RuntimeExecutionPlan
from .runtime_execution_context import RuntimeExecutionContext
from .runtime_execution_composition_descriptor import RuntimeExecutionCompositionDescriptor

class RuntimeExecutionCompositionFactory:
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
    def create(
        execution_id: str,
        runtime_id: str,
        graph_id: str,
        plan_id: str,
        context_id: str,
        composition_id: str,
        execution_identity: RuntimeExecutionIdentity,
        execution_graph: RuntimeExecutionGraph,
        execution_plan: RuntimeExecutionPlan,
        execution_context: RuntimeExecutionContext,
        identity_lookup: Optional[Dict[str, RuntimeExecutionIdentity]] = None,
        graph_lookup: Optional[Dict[str, RuntimeExecutionGraph]] = None,
        plan_lookup: Optional[Dict[str, RuntimeExecutionPlan]] = None,
        context_lookup: Optional[Dict[str, RuntimeExecutionContext]] = None,
        descriptor_lookup: Optional[Dict[str, RuntimeExecutionCompositionDescriptor]] = None,
        composition_lookup: Optional[Dict[str, Any]] = None,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        tags: Optional[Set[str]] = None,
        version: str = "1.0.0",
        schema_version: str = "1.0.0"
    ) -> RuntimeExecutionComposition:
        
        identity = ExecutionCompositionFactory.create(
            execution_id=execution_id,
            runtime_id=runtime_id,
            graph_id=graph_id,
            plan_id=plan_id,
            context_id=context_id,
            composition_id=composition_id,
            execution_identity=execution_identity,
            execution_graph=execution_graph,
            execution_plan=execution_plan,
            execution_context=execution_context,
            identity_lookup=identity_lookup,
            graph_lookup=graph_lookup,
            plan_lookup=plan_lookup,
            context_lookup=context_lookup,
            descriptor_lookup=descriptor_lookup,
            composition_lookup=composition_lookup,
            labels=labels,
            annotations=annotations,
            tags=tags,
            version=version,
            schema_version=schema_version
        )
        
        composition = RuntimeExecutionComposition(
            identifier=composition_id,
            identity=identity
        )
        
        RuntimeExecutionCompositionValidator.validate(composition)
        
        return composition
