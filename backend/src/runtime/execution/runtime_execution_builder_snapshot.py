from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionBuilderSnapshot:
    descriptor_hash: str
    composition_hash: str
    composition_lookup_hash: str
    descriptor_lookup_hash: str
    builder_lookup_hash: str
    metadata_hash: str
    statistics_hash: str
    builder_hash: str
