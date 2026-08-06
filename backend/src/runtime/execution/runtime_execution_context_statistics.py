from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionContextStatistics:
    variable_count: int
    binding_count: int
    required_variable_count: int
    optional_variable_count: int
    variable_lookup_count: int
    binding_lookup_count: int
    descriptor_lookup_count: int
    context_lookup_count: int
