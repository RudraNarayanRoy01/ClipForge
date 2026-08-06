from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionSchedulerSnapshot:
    descriptor_hash: str
    lifecycle_hash: str
    lifecycle_lookup_hash: str
    descriptor_lookup_hash: str
    scheduler_lookup_hash: str
    metadata_hash: str
    statistics_hash: str
    scheduler_hash: str
