from types import MappingProxyType
from typing import Any, Dict, Set

from .runtime_execution_builder import RuntimeExecutionBuilder
from .runtime_execution_lifecycle import RuntimeExecutionLifecycle

from .execution_lifecycle_descriptor_factory import ExecutionLifecycleDescriptorFactory
from .execution_lifecycle_metadata_factory import ExecutionLifecycleMetadataFactory
from .execution_lifecycle_statistics_builder import ExecutionLifecycleStatisticsBuilder
from .execution_lifecycle_snapshot_factory import ExecutionLifecycleSnapshotFactory
from .execution_lifecycle_factory import ExecutionLifecycleFactory

class RuntimeExecutionLifecycleFactory:
    """
    ONLY performs structural construction.
    Performs NO:
    - Execution
    - Scheduling
    - Lifecycle Behaviour
    - Monitoring
    - Telemetry
    - Optimization
    - Provider Loading
    - Hardware Management
    - Routing
    - Planning
    """

    @staticmethod
    def build(
        identifier: str,
        execution_id: str,
        runtime_id: str,
        graph_id: str,
        plan_id: str,
        context_id: str,
        composition_id: str,
        builder_id: str,
        version: str,
        schema_version: str,
        labels: Dict[str, str],
        annotations: Dict[str, str],
        tags: Set[str],
        builder: RuntimeExecutionBuilder
    ) -> RuntimeExecutionLifecycle:
        
        descriptor = ExecutionLifecycleDescriptorFactory.create(
            execution_id=execution_id,
            runtime_id=runtime_id,
            graph_id=graph_id,
            plan_id=plan_id,
            context_id=context_id,
            composition_id=composition_id,
            builder_id=builder_id,
            lifecycle_id=identifier,
            version=version,
            schema_version=schema_version
        )
        
        metadata = ExecutionLifecycleMetadataFactory.create(
            labels=labels,
            annotations=annotations,
            tags=tags
        )
        
        builder_lookup = MappingProxyType({builder.identifier: builder})
        descriptor_lookup = MappingProxyType({descriptor.lifecycle_id: descriptor})
        lifecycle_lookup = MappingProxyType({identifier: "lifecycle_placeholder"})
        
        statistics = ExecutionLifecycleStatisticsBuilder.build(
            builder=builder,
            builder_lookup=builder_lookup,
            descriptor_lookup=descriptor_lookup,
            lifecycle_lookup=lifecycle_lookup
        )
        
        snapshot = ExecutionLifecycleSnapshotFactory.create(
            descriptor=descriptor,
            builder=builder,
            builder_lookup=dict(builder_lookup),
            descriptor_lookup=dict(descriptor_lookup),
            lifecycle_lookup=dict(lifecycle_lookup),
            metadata=metadata,
            statistics=statistics
        )
        
        return ExecutionLifecycleFactory.create(
            identifier=identifier,
            descriptor=descriptor,
            metadata=metadata,
            statistics=statistics,
            snapshot=snapshot,
            runtime_execution_builder=builder,
            builder_lookup=builder_lookup,
            descriptor_lookup=descriptor_lookup,
            lifecycle_lookup=lifecycle_lookup
        )
