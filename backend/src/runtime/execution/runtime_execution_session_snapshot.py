from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionSessionSnapshot:
    descriptor_hash: str
    descriptor_lookup_hash: str
    session_lookup_hash: str
    metadata_hash: str
    statistics_hash: str
    session_hash: str
