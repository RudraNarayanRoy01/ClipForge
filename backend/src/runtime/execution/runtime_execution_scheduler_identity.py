from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .runtime_execution_scheduler_descriptor import RuntimeExecutionSchedulerDescriptor
from .runtime_execution_scheduler_metadata import RuntimeExecutionSchedulerMetadata
from .runtime_execution_scheduler_statistics import RuntimeExecutionSchedulerStatistics
from .runtime_execution_scheduler_snapshot import RuntimeExecutionSchedulerSnapshot
from .runtime_execution_lifecycle import RuntimeExecutionLifecycle

@dataclass(frozen=True)
class RuntimeExecutionSchedulerIdentity:
    descriptor: RuntimeExecutionSchedulerDescriptor
    metadata: RuntimeExecutionSchedulerMetadata
    statistics: RuntimeExecutionSchedulerStatistics
    snapshot: RuntimeExecutionSchedulerSnapshot
    runtime_execution_lifecycle: RuntimeExecutionLifecycle
    lifecycle_lookup: MappingProxyType[str, RuntimeExecutionLifecycle]
    descriptor_lookup: MappingProxyType[str, Any]
    scheduler_lookup: MappingProxyType[str, Any]
