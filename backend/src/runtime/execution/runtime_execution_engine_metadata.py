from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

@dataclass(frozen=True)
class RuntimeExecutionEngineMetadata:
    labels: MappingProxyType[str, str]
    annotations: MappingProxyType[str, str]
    tags: frozenset[str]
