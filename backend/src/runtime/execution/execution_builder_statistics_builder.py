from .runtime_execution_builder_statistics import RuntimeExecutionBuilderStatistics
from .runtime_execution_composition import RuntimeExecutionComposition
from types import MappingProxyType
from typing import Any

class ExecutionBuilderStatisticsBuilder:
    """
    ONLY performs structural construction.
    Performs NO Execution, Scheduling, Lifecycle, Telemetry, Monitoring, Optimization, Provider Loading, Hardware Management, Routing, Planning.
    """
    
    @staticmethod
    def build(
        composition: RuntimeExecutionComposition,
        composition_lookup: MappingProxyType[str, RuntimeExecutionComposition],
        descriptor_lookup: MappingProxyType[str, Any],
        builder_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionBuilderStatistics:
        return RuntimeExecutionBuilderStatistics(
            composition_count=1 if composition else 0,
            composition_lookup_count=len(composition_lookup),
            descriptor_lookup_count=len(descriptor_lookup),
            builder_lookup_count=len(builder_lookup)
        )
