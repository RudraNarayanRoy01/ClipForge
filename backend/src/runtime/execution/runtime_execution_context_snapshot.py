from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionContextSnapshot:
    descriptor_hash: str
    variable_hash: str
    binding_hash: str
    variable_lookup_hash: str
    binding_lookup_hash: str
    descriptor_lookup_hash: str
    context_lookup_hash: str
    metadata_hash: str
    statistics_hash: str
    context_hash: str
