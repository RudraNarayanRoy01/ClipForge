from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionLifecycleSnapshot:
    descriptor_hash: str
    builder_hash: str
    builder_lookup_hash: str
    descriptor_lookup_hash: str
    lifecycle_lookup_hash: str
    metadata_hash: str
    statistics_hash: str
    lifecycle_hash: str
