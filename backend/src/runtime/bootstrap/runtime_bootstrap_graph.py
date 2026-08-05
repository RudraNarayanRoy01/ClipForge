"""
Runtime Bootstrap Graph.

Canonical immutable representation of bootstrap topology.
Contains zero execution, zero scheduling, and zero planning.
"""
from dataclasses import dataclass
from typing import Tuple, FrozenSet
from types import MappingProxyType

from .runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor
from .runtime_bootstrap_layer import RuntimeBootstrapLayer


@dataclass(frozen=True)
class RuntimeBootstrapGraph:
    """
    Immutable representation of the bootstrap graph topology.
    Exposes explicit immutable lookup structures for deterministic traversal.
    """
    _roots: FrozenSet[str]
    _leaves: FrozenSet[str]
    _descriptor_lookup: MappingProxyType[str, RuntimeBootstrapDescriptor]
    _dependency_lookup: MappingProxyType[str, Tuple[str, ...]]
    _layer_lookup: MappingProxyType[str, RuntimeBootstrapLayer]
    _adjacency_lookup: MappingProxyType[str, Tuple[str, ...]]
    _reverse_adjacency_lookup: MappingProxyType[str, Tuple[str, ...]]

    def __init__(
        self,
        roots: FrozenSet[str],
        leaves: FrozenSet[str],
        descriptor_lookup: MappingProxyType[str, RuntimeBootstrapDescriptor],
        dependency_lookup: MappingProxyType[str, Tuple[str, ...]],
        layer_lookup: MappingProxyType[str, RuntimeBootstrapLayer],
        adjacency_lookup: MappingProxyType[str, Tuple[str, ...]],
        reverse_adjacency_lookup: MappingProxyType[str, Tuple[str, ...]]
    ):
        object.__setattr__(self, "_roots", frozenset(roots))
        object.__setattr__(self, "_leaves", frozenset(leaves))
        object.__setattr__(self, "_descriptor_lookup", MappingProxyType(dict(descriptor_lookup)))
        object.__setattr__(self, "_dependency_lookup", MappingProxyType(dict(dependency_lookup)))
        object.__setattr__(self, "_layer_lookup", MappingProxyType(dict(layer_lookup)))
        object.__setattr__(self, "_adjacency_lookup", MappingProxyType(dict(adjacency_lookup)))
        object.__setattr__(self, "_reverse_adjacency_lookup", MappingProxyType(dict(reverse_adjacency_lookup)))

    @property
    def roots(self) -> FrozenSet[str]:
        return self._roots

    @property
    def leaves(self) -> FrozenSet[str]:
        return self._leaves

    @property
    def descriptor_lookup(self) -> MappingProxyType[str, RuntimeBootstrapDescriptor]:
        return self._descriptor_lookup

    @property
    def dependency_lookup(self) -> MappingProxyType[str, Tuple[str, ...]]:
        return self._dependency_lookup

    @property
    def layer_lookup(self) -> MappingProxyType[str, RuntimeBootstrapLayer]:
        return self._layer_lookup

    @property
    def adjacency_lookup(self) -> MappingProxyType[str, Tuple[str, ...]]:
        return self._adjacency_lookup

    @property
    def reverse_adjacency_lookup(self) -> MappingProxyType[str, Tuple[str, ...]]:
        return self._reverse_adjacency_lookup

    def __hash__(self) -> int:
        return hash((
            self._roots,
            self._leaves,
            frozenset(self._descriptor_lookup.items()),
            frozenset(self._dependency_lookup.items()),
            frozenset(self._layer_lookup.items()),
            frozenset(self._adjacency_lookup.items()),
            frozenset(self._reverse_adjacency_lookup.items())
        ))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuntimeBootstrapGraph):
            return False
        return (
            self._roots == other._roots and
            self._leaves == other._leaves and
            dict(self._descriptor_lookup) == dict(other._descriptor_lookup) and
            dict(self._dependency_lookup) == dict(other._dependency_lookup) and
            dict(self._layer_lookup) == dict(other._layer_lookup) and
            dict(self._adjacency_lookup) == dict(other._adjacency_lookup) and
            dict(self._reverse_adjacency_lookup) == dict(other._reverse_adjacency_lookup)
        )
