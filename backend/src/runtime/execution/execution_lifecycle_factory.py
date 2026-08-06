from types import MappingProxyType
from typing import Any

from .runtime_execution_lifecycle import RuntimeExecutionLifecycle
from .runtime_execution_lifecycle_identity import RuntimeExecutionLifecycleIdentity
from .runtime_execution_lifecycle_descriptor import RuntimeExecutionLifecycleDescriptor
from .runtime_execution_lifecycle_metadata import RuntimeExecutionLifecycleMetadata
from .runtime_execution_lifecycle_statistics import RuntimeExecutionLifecycleStatistics
from .runtime_execution_lifecycle_snapshot import RuntimeExecutionLifecycleSnapshot
from .runtime_execution_builder import RuntimeExecutionBuilder

class ExecutionLifecycleFactory:
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
    def create(
        identifier: str,
        descriptor: RuntimeExecutionLifecycleDescriptor,
        metadata: RuntimeExecutionLifecycleMetadata,
        statistics: RuntimeExecutionLifecycleStatistics,
        snapshot: RuntimeExecutionLifecycleSnapshot,
        runtime_execution_builder: RuntimeExecutionBuilder,
        builder_lookup: MappingProxyType[str, RuntimeExecutionBuilder],
        descriptor_lookup: MappingProxyType[str, Any],
        lifecycle_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionLifecycle:
        
        identity = RuntimeExecutionLifecycleIdentity(
            descriptor=descriptor,
            metadata=metadata,
            statistics=statistics,
            snapshot=snapshot,
            runtime_execution_builder=runtime_execution_builder,
            builder_lookup=builder_lookup,
            descriptor_lookup=descriptor_lookup,
            lifecycle_lookup=lifecycle_lookup
        )
        
        return RuntimeExecutionLifecycle(
            identifier=identifier,
            identity=identity
        )
