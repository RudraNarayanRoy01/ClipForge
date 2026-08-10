from types import MappingProxyType
from typing import Any
from .runtime_execution_state_statistics import RuntimeExecutionStateStatistics
from .runtime_execution_session import RuntimeExecutionSession

class ExecutionStateStatisticsBuilder:
    @staticmethod
    def build(
        runtime_execution_session: RuntimeExecutionSession,
        session_lookup: MappingProxyType[str, RuntimeExecutionSession],
        descriptor_lookup: MappingProxyType[str, Any],
        state_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionStateStatistics:
        session_count = 1 if runtime_execution_session else 0
        return RuntimeExecutionStateStatistics(
            session_count=session_count,
            session_lookup_count=len(session_lookup),
            descriptor_lookup_count=len(descriptor_lookup),
            state_lookup_count=len(state_lookup)
        )
