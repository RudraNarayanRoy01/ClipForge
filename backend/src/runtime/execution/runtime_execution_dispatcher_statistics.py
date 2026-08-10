from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionDispatcherStatistics:
    state_count: int
    state_lookup_count: int
    descriptor_lookup_count: int
    dispatcher_lookup_count: int
