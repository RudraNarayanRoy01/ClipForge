"""
Runtime Bootstrap Metadata.

Canonical immutable representation of bootstrap composition metadata.
Contains versioning, timestamps, labels, and descriptive information.
"""
from dataclasses import dataclass
from types import MappingProxyType
from typing import Optional


@dataclass(frozen=True)
class RuntimeBootstrapMetadata:
    """
    Immutable representation of all metadata associated with the Bootstrap Foundation.
    Absorbs descriptive metadata that was removed from the descriptor.
    """
    _created_at_utc: float
    _version: str
    _schema_version: str
    _labels: MappingProxyType[str, str]
    _annotations: MappingProxyType[str, str]
    _description: Optional[str]

    def __init__(
        self,
        created_at_utc: float,
        version: str,
        schema_version: str,
        labels: MappingProxyType[str, str],
        annotations: MappingProxyType[str, str],
        description: Optional[str] = None
    ):
        object.__setattr__(self, "_created_at_utc", created_at_utc)
        object.__setattr__(self, "_version", version)
        object.__setattr__(self, "_schema_version", schema_version)
        object.__setattr__(self, "_labels", MappingProxyType(dict(labels)))
        object.__setattr__(self, "_annotations", MappingProxyType(dict(annotations)))
        object.__setattr__(self, "_description", description)

    @property
    def created_at_utc(self) -> float:
        return self._created_at_utc

    @property
    def version(self) -> str:
        return self._version

    @property
    def schema_version(self) -> str:
        return self._schema_version

    @property
    def labels(self) -> MappingProxyType[str, str]:
        return self._labels

    @property
    def annotations(self) -> MappingProxyType[str, str]:
        return self._annotations

    @property
    def description(self) -> Optional[str]:
        return self._description

    def __hash__(self) -> int:
        return hash((
            self._created_at_utc,
            self._version,
            self._schema_version,
            frozenset(self._labels.items()),
            frozenset(self._annotations.items()),
            self._description
        ))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuntimeBootstrapMetadata):
            return False
        return (
            self._created_at_utc == other._created_at_utc and
            self._version == other._version and
            self._schema_version == other._schema_version and
            dict(self._labels) == dict(other._labels) and
            dict(self._annotations) == dict(other._annotations) and
            self._description == other._description
        )
