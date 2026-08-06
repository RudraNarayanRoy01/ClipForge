from types import MappingProxyType
from typing import Any
from .runtime_execution_scheduler_statistics import RuntimeExecutionSchedulerStatistics
from .runtime_execution_lifecycle import RuntimeExecutionLifecycle

class ExecutionSchedulerStatisticsBuilder:
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
    def build(
        runtime_execution_lifecycle: RuntimeExecutionLifecycle,
        lifecycle_lookup: MappingProxyType[str, RuntimeExecutionLifecycle],
        descriptor_lookup: MappingProxyType[str, Any],
        scheduler_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionSchedulerStatistics:
        return RuntimeExecutionSchedulerStatistics(
            lifecycle_count=1 if runtime_execution_lifecycle else 0,
            lifecycle_lookup_count=len(lifecycle_lookup),
            descriptor_lookup_count=len(descriptor_lookup),
            scheduler_lookup_count=len(scheduler_lookup)
        )
