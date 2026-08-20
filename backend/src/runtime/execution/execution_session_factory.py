from types import MappingProxyType
from typing import Any
from .runtime_execution_session import RuntimeExecutionSession
from .runtime_execution_session_identity import RuntimeExecutionSessionIdentity
from .runtime_execution_session_descriptor import RuntimeExecutionSessionDescriptor
from .runtime_execution_session_metadata import RuntimeExecutionSessionMetadata
from .runtime_execution_session_statistics import RuntimeExecutionSessionStatistics
from .runtime_execution_session_snapshot import RuntimeExecutionSessionSnapshot

class ExecutionSessionFactory:
    @staticmethod
    def create(
        identifier: str,
        descriptor: RuntimeExecutionSessionDescriptor,
        metadata: RuntimeExecutionSessionMetadata,
        statistics: RuntimeExecutionSessionStatistics,
        snapshot: RuntimeExecutionSessionSnapshot,
        descriptor_lookup: MappingProxyType[str, Any],
        session_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionSession:
        identity = RuntimeExecutionSessionIdentity(
            descriptor=descriptor,
            metadata=metadata,
            statistics=statistics,
            snapshot=snapshot,
            descriptor_lookup=descriptor_lookup,
            session_lookup=session_lookup
        )
        return RuntimeExecutionSession(
            identifier=identifier,
            identity=identity
        )
