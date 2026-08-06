from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionEngineStatistics:
    scheduler_count: int
    scheduler_lookup_count: int
    descriptor_lookup_count: int
    engine_lookup_count: int
