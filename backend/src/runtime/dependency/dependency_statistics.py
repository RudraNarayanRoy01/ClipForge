"""
Dependency Statistics model.

Immutable metrics observation for a snapshot of the graph.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class DependencyStatistics:
    """
    Immutable snapshot of graph statistics.
    """
    node_count: int
    edge_count: int
    root_count: int
    leaf_count: int
    isolated_node_count: int
    required_dependency_count: int
    optional_dependency_count: int
    average_dependencies: float
    average_dependents: float
