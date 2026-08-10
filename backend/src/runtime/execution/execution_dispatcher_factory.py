from types import MappingProxyType
from typing import Any
from .runtime_execution_dispatcher import RuntimeExecutionDispatcher
from .runtime_execution_dispatcher_identity import RuntimeExecutionDispatcherIdentity
from .runtime_execution_dispatcher_descriptor import RuntimeExecutionDispatcherDescriptor
from .runtime_execution_dispatcher_metadata import RuntimeExecutionDispatcherMetadata
from .runtime_execution_dispatcher_statistics import RuntimeExecutionDispatcherStatistics
from .runtime_execution_dispatcher_snapshot import RuntimeExecutionDispatcherSnapshot
from .runtime_execution_state import RuntimeExecutionState

class ExecutionDispatcherFactory:
    @staticmethod
    def create(
        identifier: str,
        descriptor: RuntimeExecutionDispatcherDescriptor,
        metadata: RuntimeExecutionDispatcherMetadata,
        statistics: RuntimeExecutionDispatcherStatistics,
        snapshot: RuntimeExecutionDispatcherSnapshot,
        runtime_execution_state: RuntimeExecutionState,
        state_lookup: MappingProxyType[str, Any],
        descriptor_lookup: MappingProxyType[str, Any],
        dispatcher_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionDispatcher:
        identity = RuntimeExecutionDispatcherIdentity(
            descriptor=descriptor,
            metadata=metadata,
            statistics=statistics,
            snapshot=snapshot,
            runtime_execution_state=runtime_execution_state,
            state_lookup=state_lookup,
            descriptor_lookup=descriptor_lookup,
            dispatcher_lookup=dispatcher_lookup
        )
        return RuntimeExecutionDispatcher(
            identifier=identifier,
            identity=identity
        )
