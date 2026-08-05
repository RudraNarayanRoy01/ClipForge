"""
Runtime Bootstrap Composition.

Canonical immutable representation of the Runtime Bootstrap phase.
Owns Graph, Plan, Metadata, Graph Statistics, Bootstrap Statistics, and Snapshot.
"""
from dataclasses import dataclass

from .runtime_bootstrap_graph import RuntimeBootstrapGraph
from .runtime_bootstrap_plan import RuntimeBootstrapPlan
from .runtime_bootstrap_metadata import RuntimeBootstrapMetadata
from .bootstrap_graph_statistics import BootstrapGraphStatistics
from .runtime_bootstrap_statistics import RuntimeBootstrapStatistics
from .runtime_bootstrap_snapshot import RuntimeBootstrapSnapshot


@dataclass(frozen=True)
class RuntimeBootstrapComposition:
    """
    Immutable representation of the canonical Runtime Bootstrap Foundation.
    
    Owns ONLY:
    - RuntimeBootstrapGraph
    - RuntimeBootstrapPlan
    - RuntimeBootstrapMetadata
    - BootstrapGraphStatistics
    - RuntimeBootstrapStatistics
    - RuntimeBootstrapSnapshot
    
    Does NOT own:
    - RuntimeBootstrapState
    - RuntimeBootstrapDescriptor
    - RuntimeBootstrap identity
    - Runtime execution
    - Runtime lifecycle
    - Provider state
    - Execution state
    """
    _composition_id: str
    _graph: RuntimeBootstrapGraph
    _plan: RuntimeBootstrapPlan
    _metadata: RuntimeBootstrapMetadata
    _graph_statistics: BootstrapGraphStatistics
    _statistics: RuntimeBootstrapStatistics
    _snapshot: RuntimeBootstrapSnapshot

    def __init__(
        self,
        composition_id: str,
        graph: RuntimeBootstrapGraph,
        plan: RuntimeBootstrapPlan,
        metadata: RuntimeBootstrapMetadata,
        graph_statistics: BootstrapGraphStatistics,
        statistics: RuntimeBootstrapStatistics,
        snapshot: RuntimeBootstrapSnapshot
    ):
        object.__setattr__(self, "_composition_id", composition_id)
        object.__setattr__(self, "_graph", graph)
        object.__setattr__(self, "_plan", plan)
        object.__setattr__(self, "_metadata", metadata)
        object.__setattr__(self, "_graph_statistics", graph_statistics)
        object.__setattr__(self, "_statistics", statistics)
        object.__setattr__(self, "_snapshot", snapshot)

    @property
    def composition_id(self) -> str:
        return self._composition_id

    @property
    def graph(self) -> RuntimeBootstrapGraph:
        return self._graph

    @property
    def plan(self) -> RuntimeBootstrapPlan:
        return self._plan

    @property
    def metadata(self) -> RuntimeBootstrapMetadata:
        return self._metadata

    @property
    def graph_statistics(self) -> BootstrapGraphStatistics:
        return self._graph_statistics

    @property
    def statistics(self) -> RuntimeBootstrapStatistics:
        return self._statistics

    @property
    def snapshot(self) -> RuntimeBootstrapSnapshot:
        return self._snapshot

    def __hash__(self) -> int:
        return hash((
            self._composition_id,
            self._graph,
            self._plan,
            self._metadata,
            self._graph_statistics,
            self._statistics,
            self._snapshot
        ))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuntimeBootstrapComposition):
            return False
        return (
            self._composition_id == other._composition_id and
            self._graph == other._graph and
            self._plan == other._plan and
            self._metadata == other._metadata and
            self._graph_statistics == other._graph_statistics and
            self._statistics == other._statistics and
            self._snapshot == other._snapshot
        )
