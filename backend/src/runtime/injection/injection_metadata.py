"""
Injection Metadata.

Immutable metadata for the Runtime Injection Foundation.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class InjectionMetadata:
    """
    Immutable representation of injection metadata.
    Tracks versioning and temporal properties of the injection blueprint.
    """
    schema_version: str
    builder_version: str
    creation_timestamp: float
    metadata_mapping: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))
