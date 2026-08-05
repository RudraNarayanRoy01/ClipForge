from dataclasses import dataclass

@dataclass(frozen=True)
class ResolutionStatistics:
    """
    Immutable statistics for a Runtime Resolution.
    
    Computed observationally based on the topological structure of the dependency graph.
    Contains no execution or performance metrics.
    """
    total_components: int
    total_dependencies: int
    root_nodes: int
    leaf_nodes: int
    disconnected_groups: int
    maximum_dependency_depth: int
    average_dependency_depth: float
