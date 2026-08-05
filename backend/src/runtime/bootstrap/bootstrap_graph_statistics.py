"""
Bootstrap Graph Statistics.

Canonical immutable representation of graph topology metrics.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class BootstrapGraphStatistics:
    """
    Immutable representation of graph topology statistics.
    Contains ONLY structural graph metrics.
    """
    _node_count: int
    _edge_count: int
    _root_count: int
    _leaf_count: int
    _graph_depth: int
    _graph_width: int
    _connected_components: int

    def __init__(
        self,
        node_count: int,
        edge_count: int,
        root_count: int,
        leaf_count: int,
        graph_depth: int,
        graph_width: int,
        connected_components: int
    ):
        object.__setattr__(self, "_node_count", node_count)
        object.__setattr__(self, "_edge_count", edge_count)
        object.__setattr__(self, "_root_count", root_count)
        object.__setattr__(self, "_leaf_count", leaf_count)
        object.__setattr__(self, "_graph_depth", graph_depth)
        object.__setattr__(self, "_graph_width", graph_width)
        object.__setattr__(self, "_connected_components", connected_components)

    @property
    def node_count(self) -> int:
        return self._node_count

    @property
    def edge_count(self) -> int:
        return self._edge_count

    @property
    def root_count(self) -> int:
        return self._root_count

    @property
    def leaf_count(self) -> int:
        return self._leaf_count

    @property
    def graph_depth(self) -> int:
        return self._graph_depth

    @property
    def graph_width(self) -> int:
        return self._graph_width

    @property
    def connected_components(self) -> int:
        return self._connected_components
