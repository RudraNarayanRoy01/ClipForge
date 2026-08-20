from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionSessionStatistics:
    descriptor_lookup_count: int
    session_lookup_count: int
