from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .runtime_execution_builder_descriptor import RuntimeExecutionBuilderDescriptor
from .runtime_execution_builder_metadata import RuntimeExecutionBuilderMetadata
from .runtime_execution_builder_statistics import RuntimeExecutionBuilderStatistics
from .runtime_execution_builder_snapshot import RuntimeExecutionBuilderSnapshot
from .runtime_execution_composition import RuntimeExecutionComposition

@dataclass(frozen=True)
class RuntimeExecutionBuilderIdentity:
    descriptor: RuntimeExecutionBuilderDescriptor
    metadata: RuntimeExecutionBuilderMetadata
    statistics: RuntimeExecutionBuilderStatistics
    snapshot: RuntimeExecutionBuilderSnapshot
    composition: RuntimeExecutionComposition
    composition_lookup: MappingProxyType[str, RuntimeExecutionComposition]
    descriptor_lookup: MappingProxyType[str, RuntimeExecutionBuilderDescriptor]
    builder_lookup: MappingProxyType[str, Any]
