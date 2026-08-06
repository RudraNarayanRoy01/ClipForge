from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionSnapshot:
    execution_hash: str
    identity_hash: str
    descriptor_hash: str
    metadata_hash: str
    state_hash: str
    composition_hash: str
