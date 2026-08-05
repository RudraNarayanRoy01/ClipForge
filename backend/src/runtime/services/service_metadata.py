"""
Service metadata.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Any
from datetime import datetime, timezone

@dataclass(frozen=True)
class ServiceMetadata:
    """Immutable metadata for a Service Composition."""
    schema_version: str
    builder_version: str
    creation_timestamp: float = field(default_factory=lambda: datetime.now(timezone.utc).timestamp())
    metadata_mapping: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self):
        if not isinstance(self.metadata_mapping, MappingProxyType):
            object.__setattr__(self, "metadata_mapping", MappingProxyType(dict(self.metadata_mapping)))
