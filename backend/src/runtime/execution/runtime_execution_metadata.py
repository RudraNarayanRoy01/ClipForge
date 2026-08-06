from dataclasses import dataclass
from types import MappingProxyType
from datetime import datetime

@dataclass(frozen=True)
class RuntimeExecutionMetadata:
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    tags: frozenset[str]
    annotations: MappingProxyType[str, str]
    metadata_version: str
