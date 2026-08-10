from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionSessionStatistics:
    engine_count: int
    engine_lookup_count: int
    descriptor_lookup_count: int
    session_lookup_count: int
