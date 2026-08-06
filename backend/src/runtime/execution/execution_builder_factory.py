from types import MappingProxyType
from typing import Any

from .runtime_execution_builder_identity import RuntimeExecutionBuilderIdentity
from .runtime_execution_builder_descriptor import RuntimeExecutionBuilderDescriptor
from .runtime_execution_builder_metadata import RuntimeExecutionBuilderMetadata
from .runtime_execution_builder_statistics import RuntimeExecutionBuilderStatistics
from .runtime_execution_builder_snapshot import RuntimeExecutionBuilderSnapshot
from .runtime_execution_composition import RuntimeExecutionComposition

class ExecutionBuilderFactory:
    """
    ONLY performs structural construction.
    Performs NO Execution, Scheduling, Lifecycle, Telemetry, Monitoring, Optimization, Provider Loading, Hardware Management, Routing, Planning.
    """
    
    @staticmethod
    def create(
        descriptor: RuntimeExecutionBuilderDescriptor,
        metadata: RuntimeExecutionBuilderMetadata,
        statistics: RuntimeExecutionBuilderStatistics,
        snapshot: RuntimeExecutionBuilderSnapshot,
        composition: RuntimeExecutionComposition,
        composition_lookup: MappingProxyType[str, RuntimeExecutionComposition],
        descriptor_lookup: MappingProxyType[str, RuntimeExecutionBuilderDescriptor],
        builder_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionBuilderIdentity:
        return RuntimeExecutionBuilderIdentity(
            descriptor=descriptor,
            metadata=metadata,
            statistics=statistics,
            snapshot=snapshot,
            composition=composition,
            composition_lookup=composition_lookup,
            descriptor_lookup=descriptor_lookup,
            builder_lookup=builder_lookup
        )
