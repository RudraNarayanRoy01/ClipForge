from types import MappingProxyType
from typing import Any
from .runtime_execution_session_statistics import RuntimeExecutionSessionStatistics

class ExecutionSessionStatisticsBuilder:
    @staticmethod
    def build(
        descriptor_lookup: MappingProxyType[str, Any],
        session_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionSessionStatistics:
        return RuntimeExecutionSessionStatistics(
            descriptor_lookup_count=len(descriptor_lookup),
            session_lookup_count=len(session_lookup)
        )
