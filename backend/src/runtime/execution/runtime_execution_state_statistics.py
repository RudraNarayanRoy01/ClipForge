from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionStateStatistics:
    session_count: int
    session_lookup_count: int
    descriptor_lookup_count: int
    state_lookup_count: int
