from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .runtime_execution_dispatcher_descriptor import RuntimeExecutionDispatcherDescriptor
from .runtime_execution_dispatcher_metadata import RuntimeExecutionDispatcherMetadata
from .runtime_execution_dispatcher_statistics import RuntimeExecutionDispatcherStatistics
from .runtime_execution_dispatcher_snapshot import RuntimeExecutionDispatcherSnapshot
from .runtime_execution_state import RuntimeExecutionState

@dataclass(frozen=True)
class RuntimeExecutionDispatcherIdentity:
    descriptor: RuntimeExecutionDispatcherDescriptor
    metadata: RuntimeExecutionDispatcherMetadata
    statistics: RuntimeExecutionDispatcherStatistics
    snapshot: RuntimeExecutionDispatcherSnapshot
    runtime_execution_state: RuntimeExecutionState
    state_lookup: MappingProxyType[str, Any]
    descriptor_lookup: MappingProxyType[str, Any]
    dispatcher_lookup: MappingProxyType[str, Any]
