from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionStateSnapshot:
    descriptor_hash: str
    session_hash: str
    session_lookup_hash: str
    descriptor_lookup_hash: str
    state_lookup_hash: str
    metadata_hash: str
    statistics_hash: str
    state_hash: str
