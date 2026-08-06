from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionSchedulerStatistics:
    lifecycle_count: int
    lifecycle_lookup_count: int
    descriptor_lookup_count: int
    scheduler_lookup_count: int
