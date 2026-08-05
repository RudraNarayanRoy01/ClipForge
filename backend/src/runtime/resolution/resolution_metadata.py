from dataclasses import dataclass, field
from typing import Mapping
from types import MappingProxyType

@dataclass(frozen=True)
class ResolutionMetadata:
    """
    Immutable metadata for a Runtime Resolution.
    
    Contains execution-independent schema and timestamps.
    """
    schema_version: str
    resolver_version: str
    runtime_version: str
    timestamp: float
    resolution_uuid: str
    additional_info: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))
