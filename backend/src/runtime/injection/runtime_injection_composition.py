"""
Runtime Injection Composition.

Canonical immutable Runtime Injection Composition.
Represents the immutable dependency graph before Runtime Bootstrap.
Matches architectural vocabulary of Runtime Composition.
"""
from dataclasses import dataclass

from .injection_metadata import InjectionMetadata
from .injection_snapshot import InjectionSnapshot
from .injection_statistics import InjectionStatistics
from .runtime_injection_graph import RuntimeInjectionGraph


@dataclass(frozen=True)
class RuntimeInjectionComposition:
    """
    Immutable representation of the canonical Runtime Injection Foundation.
    Contains no behavior, no dependency injection logic, no resolution.
    Exposes read-only properties for safe architectural boundaries.
    """
    _composition_id: str
    _graph: RuntimeInjectionGraph
    _metadata: InjectionMetadata
    _statistics: InjectionStatistics
    _snapshot: InjectionSnapshot

    def __init__(
        self,
        composition_id: str,
        graph: RuntimeInjectionGraph,
        metadata: InjectionMetadata,
        statistics: InjectionStatistics,
        snapshot: InjectionSnapshot
    ):
        object.__setattr__(self, "_composition_id", composition_id)
        object.__setattr__(self, "_graph", graph)
        object.__setattr__(self, "_metadata", metadata)
        object.__setattr__(self, "_statistics", statistics)
        object.__setattr__(self, "_snapshot", snapshot)

    @property
    def composition_id(self) -> str:
        return self._composition_id

    @property
    def graph(self) -> RuntimeInjectionGraph:
        return self._graph

    @property
    def metadata(self) -> InjectionMetadata:
        return self._metadata

    @property
    def statistics(self) -> InjectionStatistics:
        return self._statistics

    @property
    def snapshot(self) -> InjectionSnapshot:
        return self._snapshot
