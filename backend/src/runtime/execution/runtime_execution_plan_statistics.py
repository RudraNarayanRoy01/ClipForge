from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionPlanStatistics:
    layer_count: int
    dependency_batch_count: int
    planned_step_count: int
    graph_depth: int
    maximum_parallel_groups: int
    node_count: int
