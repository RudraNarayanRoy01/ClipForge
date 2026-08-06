from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionGraphStatistics:
    node_count: int
    edge_count: int
    root_count: int
    leaf_count: int
    graph_depth: int
    graph_width: int
    connected_component_count: int
    isolated_node_count: int
