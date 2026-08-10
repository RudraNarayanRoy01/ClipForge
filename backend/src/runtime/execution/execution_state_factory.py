from types import MappingProxyType
from typing import Any
from .runtime_execution_state import RuntimeExecutionState
from .runtime_execution_state_identity import RuntimeExecutionStateIdentity
from .runtime_execution_state_descriptor import RuntimeExecutionStateDescriptor
from .runtime_execution_state_metadata import RuntimeExecutionStateMetadata
from .runtime_execution_state_statistics import RuntimeExecutionStateStatistics
from .runtime_execution_state_snapshot import RuntimeExecutionStateSnapshot
from .runtime_execution_session import RuntimeExecutionSession

class ExecutionStateFactory:
    @staticmethod
    def create(
        identifier: str,
        descriptor: RuntimeExecutionStateDescriptor,
        metadata: RuntimeExecutionStateMetadata,
        statistics: RuntimeExecutionStateStatistics,
        snapshot: RuntimeExecutionStateSnapshot,
        runtime_execution_session: RuntimeExecutionSession,
        session_lookup: MappingProxyType[str, RuntimeExecutionSession],
        descriptor_lookup: MappingProxyType[str, Any],
        state_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionState:
        identity = RuntimeExecutionStateIdentity(
            descriptor=descriptor,
            metadata=metadata,
            statistics=statistics,
            snapshot=snapshot,
            runtime_execution_session=runtime_execution_session,
            session_lookup=session_lookup,
            descriptor_lookup=descriptor_lookup,
            state_lookup=state_lookup
        )
        return RuntimeExecutionState(
            identifier=identifier,
            identity=identity
        )
