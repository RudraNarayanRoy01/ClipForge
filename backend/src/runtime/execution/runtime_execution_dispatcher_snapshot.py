from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionDispatcherSnapshot:
    descriptor_hash: str
    state_hash: str
    state_lookup_hash: str
    descriptor_lookup_hash: str
    dispatcher_lookup_hash: str
    metadata_hash: str
    statistics_hash: str
    dispatcher_hash: str
