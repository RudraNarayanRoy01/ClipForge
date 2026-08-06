from types import MappingProxyType
from typing import Any

from .runtime_execution_lifecycle_statistics import RuntimeExecutionLifecycleStatistics
from .runtime_execution_builder import RuntimeExecutionBuilder

class ExecutionLifecycleStatisticsBuilder:
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
        builder: RuntimeExecutionBuilder,
        builder_lookup: MappingProxyType[str, RuntimeExecutionBuilder],
        descriptor_lookup: MappingProxyType[str, Any],
        lifecycle_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionLifecycleStatistics:
        return RuntimeExecutionLifecycleStatistics(
            builder_count=1 if builder else 0,
            builder_lookup_count=len(builder_lookup),
            descriptor_lookup_count=len(descriptor_lookup),
            lifecycle_lookup_count=len(lifecycle_lookup)
        )
