from types import MappingProxyType
from typing import Any
from .runtime_execution_state import RuntimeExecutionState
from .runtime_execution_dispatcher_statistics import RuntimeExecutionDispatcherStatistics

class ExecutionDispatcherStatisticsBuilder:
    @staticmethod
    def build(
        runtime_execution_state: RuntimeExecutionState,
        state_lookup: MappingProxyType[str, Any],
        descriptor_lookup: MappingProxyType[str, Any],
        dispatcher_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionDispatcherStatistics:
        return RuntimeExecutionDispatcherStatistics(
            state_count=1 if runtime_execution_state else 0,
            state_lookup_count=len(state_lookup),
            descriptor_lookup_count=len(descriptor_lookup),
            dispatcher_lookup_count=len(dispatcher_lookup)
        )
