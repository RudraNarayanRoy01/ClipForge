from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .runtime_execution_lifecycle_descriptor import RuntimeExecutionLifecycleDescriptor
from .runtime_execution_lifecycle_metadata import RuntimeExecutionLifecycleMetadata
from .runtime_execution_lifecycle_statistics import RuntimeExecutionLifecycleStatistics
from .runtime_execution_lifecycle_snapshot import RuntimeExecutionLifecycleSnapshot
from .runtime_execution_builder import RuntimeExecutionBuilder

@dataclass(frozen=True)
class RuntimeExecutionLifecycleIdentity:
    descriptor: RuntimeExecutionLifecycleDescriptor
    metadata: RuntimeExecutionLifecycleMetadata
    statistics: RuntimeExecutionLifecycleStatistics
    snapshot: RuntimeExecutionLifecycleSnapshot
    runtime_execution_builder: RuntimeExecutionBuilder
    builder_lookup: MappingProxyType[str, RuntimeExecutionBuilder]
    descriptor_lookup: MappingProxyType[str, Any]
    lifecycle_lookup: MappingProxyType[str, Any]
