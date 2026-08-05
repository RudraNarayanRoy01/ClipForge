"""
Runtime Bootstrap Descriptor.

Canonical immutable representation of a bootstrap descriptor's identity.
Contains zero behavior and zero execution state.
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class RuntimeBootstrapDescriptor:
    """
    Immutable identity for a component in the Bootstrap Foundation.
    Contains only identifier, version, and dependency identifiers.
    Descriptive metadata (labels, annotations) belongs in RuntimeBootstrapMetadata.
    """
    _identifier: str
    _version: str
    _dependency_identifiers: Tuple[str, ...]

    def __init__(
        self,
        identifier: str,
        version: str,
        dependency_identifiers: Tuple[str, ...]
    ):
        object.__setattr__(self, "_identifier", identifier)
        object.__setattr__(self, "_version", version)
        object.__setattr__(self, "_dependency_identifiers", tuple(dependency_identifiers))

    @property
    def identifier(self) -> str:
        return self._identifier

    @property
    def version(self) -> str:
        return self._version

    @property
    def dependency_identifiers(self) -> Tuple[str, ...]:
        return self._dependency_identifiers
