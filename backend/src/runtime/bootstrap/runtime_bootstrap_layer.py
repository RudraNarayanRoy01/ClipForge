"""
Runtime Bootstrap Layer.

Canonical immutable representation of a single bootstrap layer.
Contains zero execution, zero scheduling, and zero initialization.
"""
from dataclasses import dataclass
from typing import Tuple
from types import MappingProxyType

from .runtime_bootstrap_dependency_batch import RuntimeBootstrapDependencyBatch


@dataclass(frozen=True)
class RuntimeBootstrapLayer:
    """
    Immutable representation of one declarative bootstrap layer.
    Owns ONLY layer identifier, ordered dependency batches, and immutable metadata.
    """
    _layer_identifier: str
    _dependency_batches: Tuple[RuntimeBootstrapDependencyBatch, ...]
    _layer_metadata: MappingProxyType[str, str]

    def __init__(
        self,
        layer_identifier: str,
        dependency_batches: Tuple[RuntimeBootstrapDependencyBatch, ...],
        layer_metadata: MappingProxyType[str, str]
    ):
        object.__setattr__(self, "_layer_identifier", layer_identifier)
        object.__setattr__(self, "_dependency_batches", tuple(dependency_batches))
        object.__setattr__(self, "_layer_metadata", MappingProxyType(dict(layer_metadata)))

    @property
    def layer_identifier(self) -> str:
        return self._layer_identifier

    @property
    def dependency_batches(self) -> Tuple[RuntimeBootstrapDependencyBatch, ...]:
        return self._dependency_batches

    @property
    def layer_metadata(self) -> MappingProxyType[str, str]:
        return self._layer_metadata

    def __hash__(self) -> int:
        return hash((self._layer_identifier, self._dependency_batches, frozenset(self._layer_metadata.items())))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuntimeBootstrapLayer):
            return False
        return (self._layer_identifier == other._layer_identifier and
                self._dependency_batches == other._dependency_batches and
                dict(self._layer_metadata) == dict(other._layer_metadata))
