from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionBuilderStatistics:
    composition_count: int
    composition_lookup_count: int
    descriptor_lookup_count: int
    builder_lookup_count: int
