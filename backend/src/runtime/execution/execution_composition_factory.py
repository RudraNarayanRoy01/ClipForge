from types import MappingProxyType
from typing import Dict, Set, Optional, Any

from .runtime_execution_composition_identity import RuntimeExecutionCompositionIdentity
from .execution_composition_descriptor_factory import ExecutionCompositionDescriptorFactory
from .execution_composition_metadata_factory import ExecutionCompositionMetadataFactory
from .execution_composition_statistics_builder import ExecutionCompositionStatisticsBuilder
from .execution_composition_snapshot_factory import ExecutionCompositionSnapshotFactory
from .runtime_execution_identity import RuntimeExecutionIdentity
from .runtime_execution_graph import RuntimeExecutionGraph
from .runtime_execution_plan import RuntimeExecutionPlan
from .runtime_execution_context import RuntimeExecutionContext
from .runtime_execution_composition_descriptor import RuntimeExecutionCompositionDescriptor

class ExecutionCompositionFactory:
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
    ) -> RuntimeExecutionCompositionIdentity:
        
        descriptor = ExecutionCompositionDescriptorFactory.create(
            execution_id=execution_id,
            runtime_id=runtime_id,
            graph_id=graph_id,
            plan_id=plan_id,
            context_id=context_id,
            composition_id=composition_id,
            version=version,
            schema_version=schema_version
        )
        
        metadata = ExecutionCompositionMetadataFactory.create(
            labels=labels,
            annotations=annotations,
            tags=tags
        )
        
        safe_identity_lookup = MappingProxyType(identity_lookup.copy() if identity_lookup else {})
        safe_graph_lookup = MappingProxyType(graph_lookup.copy() if graph_lookup else {})
        safe_plan_lookup = MappingProxyType(plan_lookup.copy() if plan_lookup else {})
        safe_context_lookup = MappingProxyType(context_lookup.copy() if context_lookup else {})
        safe_descriptor_lookup = MappingProxyType(descriptor_lookup.copy() if descriptor_lookup else {})
        safe_composition_lookup = MappingProxyType(composition_lookup.copy() if composition_lookup else {})
        
        statistics = ExecutionCompositionStatisticsBuilder.build(
            execution_identity=execution_identity,
            execution_graph=execution_graph,
            execution_plan=execution_plan,
            execution_context=execution_context,
            identity_lookup=safe_identity_lookup,
            graph_lookup=safe_graph_lookup,
            plan_lookup=safe_plan_lookup,
            context_lookup=safe_context_lookup,
            descriptor_lookup=safe_descriptor_lookup,
            composition_lookup=safe_composition_lookup
        )
        
        snapshot = ExecutionCompositionSnapshotFactory.create(
            descriptor=descriptor,
            metadata=metadata,
            statistics=statistics,
            execution_identity=execution_identity,
            execution_graph=execution_graph,
            execution_plan=execution_plan,
            execution_context=execution_context,
            identity_lookup=safe_identity_lookup,
            graph_lookup=safe_graph_lookup,
            plan_lookup=safe_plan_lookup,
            context_lookup=safe_context_lookup,
            descriptor_lookup=safe_descriptor_lookup,
            composition_lookup=safe_composition_lookup
        )
        
        return RuntimeExecutionCompositionIdentity(
            descriptor=descriptor,
            metadata=metadata,
            statistics=statistics,
            snapshot=snapshot,
            execution_identity=execution_identity,
            execution_graph=execution_graph,
            execution_plan=execution_plan,
            execution_context=execution_context,
            identity_lookup=safe_identity_lookup,
            graph_lookup=safe_graph_lookup,
            plan_lookup=safe_plan_lookup,
            context_lookup=safe_context_lookup,
            descriptor_lookup=safe_descriptor_lookup,
            composition_lookup=safe_composition_lookup
        )
