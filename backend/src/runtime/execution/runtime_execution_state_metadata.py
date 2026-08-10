from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

@dataclass(frozen=True)
class RuntimeExecutionStateMetadata:
    labels: MappingProxyType[str, str]
    annotations: MappingProxyType[str, str]
    tags: frozenset[str]
