from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionEngineSnapshot:
    descriptor_hash: str
    scheduler_hash: str
    scheduler_lookup_hash: str
    descriptor_lookup_hash: str
    engine_lookup_hash: str
    metadata_hash: str
    statistics_hash: str
    engine_hash: str
