"""
Runtime Bootstrap Snapshot.

Canonical immutable point-in-time snapshot of the Runtime Bootstrap state.
Contains deterministic SHA-256 hashes of the structures.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeBootstrapSnapshot:
    """
    Immutable representation of the canonical Bootstrap Snapshot.
    Stores comprehensive deterministic hashing of all structural components.
    """
    _bootstrap_hash: str
    _composition_hash: str
    _graph_hash: str
    _plan_hash: str
    _metadata_hash: str
    _statistics_hash: str
    _graph_statistics_hash: str

    def __init__(
        self,
        bootstrap_hash: str,
        composition_hash: str,
        graph_hash: str,
        plan_hash: str,
        metadata_hash: str,
        statistics_hash: str,
        graph_statistics_hash: str
    ):
        object.__setattr__(self, "_bootstrap_hash", bootstrap_hash)
        object.__setattr__(self, "_composition_hash", composition_hash)
        object.__setattr__(self, "_graph_hash", graph_hash)
        object.__setattr__(self, "_plan_hash", plan_hash)
        object.__setattr__(self, "_metadata_hash", metadata_hash)
        object.__setattr__(self, "_statistics_hash", statistics_hash)
        object.__setattr__(self, "_graph_statistics_hash", graph_statistics_hash)

    @property
    def bootstrap_hash(self) -> str:
        return self._bootstrap_hash

    @property
    def composition_hash(self) -> str:
        return self._composition_hash

    @property
    def graph_hash(self) -> str:
        return self._graph_hash

    @property
    def plan_hash(self) -> str:
        return self._plan_hash

    @property
    def metadata_hash(self) -> str:
        return self._metadata_hash

    @property
    def statistics_hash(self) -> str:
        return self._statistics_hash

    @property
    def graph_statistics_hash(self) -> str:
        return self._graph_statistics_hash
