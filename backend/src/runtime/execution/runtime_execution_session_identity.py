from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .runtime_execution_session_descriptor import RuntimeExecutionSessionDescriptor
from .runtime_execution_session_metadata import RuntimeExecutionSessionMetadata
from .runtime_execution_session_statistics import RuntimeExecutionSessionStatistics
from .runtime_execution_session_snapshot import RuntimeExecutionSessionSnapshot
from .runtime_execution_engine import RuntimeExecutionEngine

@dataclass(frozen=True)
class RuntimeExecutionSessionIdentity:
    descriptor: RuntimeExecutionSessionDescriptor
    metadata: RuntimeExecutionSessionMetadata
    statistics: RuntimeExecutionSessionStatistics
    snapshot: RuntimeExecutionSessionSnapshot
    runtime_execution_engine: RuntimeExecutionEngine
    engine_lookup: MappingProxyType[str, RuntimeExecutionEngine]
    descriptor_lookup: MappingProxyType[str, Any]
    session_lookup: MappingProxyType[str, Any]
