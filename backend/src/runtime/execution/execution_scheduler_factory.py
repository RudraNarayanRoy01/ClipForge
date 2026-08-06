from types import MappingProxyType
from typing import Any

from .runtime_execution_scheduler import RuntimeExecutionScheduler
from .runtime_execution_scheduler_identity import RuntimeExecutionSchedulerIdentity
from .runtime_execution_scheduler_descriptor import RuntimeExecutionSchedulerDescriptor
from .runtime_execution_scheduler_metadata import RuntimeExecutionSchedulerMetadata
from .runtime_execution_scheduler_statistics import RuntimeExecutionSchedulerStatistics
from .runtime_execution_scheduler_snapshot import RuntimeExecutionSchedulerSnapshot
from .runtime_execution_lifecycle import RuntimeExecutionLifecycle

class ExecutionSchedulerFactory:
    """
    ONLY performs structural construction.

    Performs NO:

    Execution
    Scheduling
    Monitoring
    Telemetry
    Optimization
    Provider Loading
    Hardware Management
    Routing
    Planning
    """
    
    @staticmethod
    def create(
        identifier: str,
        descriptor: RuntimeExecutionSchedulerDescriptor,
        metadata: RuntimeExecutionSchedulerMetadata,
        statistics: RuntimeExecutionSchedulerStatistics,
        snapshot: RuntimeExecutionSchedulerSnapshot,
        runtime_execution_lifecycle: RuntimeExecutionLifecycle,
        lifecycle_lookup: MappingProxyType[str, RuntimeExecutionLifecycle],
        descriptor_lookup: MappingProxyType[str, Any],
        scheduler_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionScheduler:
        
        identity = RuntimeExecutionSchedulerIdentity(
            descriptor=descriptor,
            metadata=metadata,
            statistics=statistics,
            snapshot=snapshot,
            runtime_execution_lifecycle=runtime_execution_lifecycle,
            lifecycle_lookup=lifecycle_lookup,
            descriptor_lookup=descriptor_lookup,
            scheduler_lookup=scheduler_lookup
        )
        
        return RuntimeExecutionScheduler(
            identifier=identifier,
            identity=identity
        )
