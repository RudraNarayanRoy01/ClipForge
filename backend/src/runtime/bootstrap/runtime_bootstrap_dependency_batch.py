"""
Runtime Bootstrap Dependency Batch.

Canonical immutable representation of a dependency batch within a bootstrap layer.
Contains zero execution, zero scheduling, and zero initialization.
"""
from dataclasses import dataclass
from typing import Tuple
from types import MappingProxyType

from .runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor


@dataclass(frozen=True, eq=False)
class RuntimeBootstrapDependencyBatch:
    """
    Immutable representation of a dependency batch within a layer.
    
    Responsibilities:
    - Groups descriptors structurally
    
    Boundaries:
    - Contains zero execution logic
    - Contains zero scheduling
    - Contains zero dependency resolution
    - Contains zero activation
    - Exists purely as immutable metadata
    """
    _batch_identifier: str
    _descriptors: Tuple[RuntimeBootstrapDescriptor, ...]
    _dependency_metadata: MappingProxyType[str, str]

    def __init__(
        self,
        batch_identifier: str,
        descriptors: Tuple[RuntimeBootstrapDescriptor, ...],
        dependency_metadata: MappingProxyType[str, str]
    ):
        object.__setattr__(self, "_batch_identifier", batch_identifier)
        object.__setattr__(self, "_descriptors", tuple(descriptors))
        object.__setattr__(self, "_dependency_metadata", MappingProxyType(dict(dependency_metadata)))

    @property
    def batch_identifier(self) -> str:
        return self._batch_identifier

    @property
    def descriptors(self) -> Tuple[RuntimeBootstrapDescriptor, ...]:
        return self._descriptors

    @property
    def dependency_metadata(self) -> MappingProxyType[str, str]:
        return self._dependency_metadata

    def __hash__(self) -> int:
        return hash((self._batch_identifier, self._descriptors, frozenset(self._dependency_metadata.items())))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuntimeBootstrapDependencyBatch):
            return False
        return (self._batch_identifier == other._batch_identifier and
                self._descriptors == other._descriptors and
                dict(self._dependency_metadata) == dict(other._dependency_metadata))
