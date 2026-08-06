from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionCompositionSnapshot:
    descriptor_hash: str
    identity_hash: str
    graph_hash: str
    plan_hash: str
    context_hash: str
    identity_lookup_hash: str
    graph_lookup_hash: str
    plan_lookup_hash: str
    context_lookup_hash: str
    descriptor_lookup_hash: str
    composition_lookup_hash: str
    metadata_hash: str
    statistics_hash: str
    composition_hash: str
