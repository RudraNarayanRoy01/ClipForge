from types import MappingProxyType
from typing import Any
from .runtime_execution_engine import RuntimeExecutionEngine
from .runtime_execution_session_statistics import RuntimeExecutionSessionStatistics

class ExecutionSessionStatisticsBuilder:
    @staticmethod
    def build(
        runtime_execution_engine: RuntimeExecutionEngine,
        engine_lookup: MappingProxyType[str, RuntimeExecutionEngine],
        descriptor_lookup: MappingProxyType[str, Any],
        session_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionSessionStatistics:
        engine_count = 1 if runtime_execution_engine is not None else 0
        return RuntimeExecutionSessionStatistics(
            engine_count=engine_count,
            engine_lookup_count=len(engine_lookup),
            descriptor_lookup_count=len(descriptor_lookup),
            session_lookup_count=len(session_lookup)
        )
