from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionLifecycleStatistics:
    builder_count: int
    builder_lookup_count: int
    descriptor_lookup_count: int
    lifecycle_lookup_count: int
