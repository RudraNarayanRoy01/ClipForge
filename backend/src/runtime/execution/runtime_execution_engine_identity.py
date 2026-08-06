from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .runtime_execution_engine_descriptor import RuntimeExecutionEngineDescriptor
from .runtime_execution_engine_metadata import RuntimeExecutionEngineMetadata
from .runtime_execution_engine_statistics import RuntimeExecutionEngineStatistics
from .runtime_execution_engine_snapshot import RuntimeExecutionEngineSnapshot
from .runtime_execution_scheduler import RuntimeExecutionScheduler

@dataclass(frozen=True)
class RuntimeExecutionEngineIdentity:
    descriptor: RuntimeExecutionEngineDescriptor
    metadata: RuntimeExecutionEngineMetadata
    statistics: RuntimeExecutionEngineStatistics
    snapshot: RuntimeExecutionEngineSnapshot
    runtime_execution_scheduler: RuntimeExecutionScheduler
    scheduler_lookup: MappingProxyType[str, RuntimeExecutionScheduler]
    descriptor_lookup: MappingProxyType[str, Any]
    engine_lookup: MappingProxyType[str, Any]
