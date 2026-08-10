from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .runtime_execution_state_descriptor import RuntimeExecutionStateDescriptor
from .runtime_execution_state_metadata import RuntimeExecutionStateMetadata
from .runtime_execution_state_statistics import RuntimeExecutionStateStatistics
from .runtime_execution_state_snapshot import RuntimeExecutionStateSnapshot
from .runtime_execution_session import RuntimeExecutionSession

@dataclass(frozen=True)
class RuntimeExecutionStateIdentity:
    descriptor: RuntimeExecutionStateDescriptor
    metadata: RuntimeExecutionStateMetadata
    statistics: RuntimeExecutionStateStatistics
    snapshot: RuntimeExecutionStateSnapshot
    runtime_execution_session: RuntimeExecutionSession
    session_lookup: MappingProxyType[str, RuntimeExecutionSession]
    descriptor_lookup: MappingProxyType[str, Any]
    state_lookup: MappingProxyType[str, Any]
