from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionCompositionStatistics:
    identity_count: int
    graph_count: int
    plan_count: int
    context_count: int
    identity_lookup_count: int
    graph_lookup_count: int
    plan_lookup_count: int
    context_lookup_count: int
    descriptor_lookup_count: int
    composition_lookup_count: int
