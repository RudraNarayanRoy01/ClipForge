"""
Runtime Injection Graph Statistics.

Immutable statistics for the graph topology only.
Maintains strict SRP by separating graph metrics from general injection metrics.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeInjectionGraphStatistics:
    """
    Purely observational statistics for the injection graph topology.
    Never evaluates Runtime quality or executes logic.
    """
    edge_count: int
    vertex_count: int
    root_count: int
    leaf_count: int
    connected_components: int
    graph_depth: int
    graph_width: int
    average_degree: float
    maximum_degree: int
    minimum_degree: int
