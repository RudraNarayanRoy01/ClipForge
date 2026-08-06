from dataclasses import dataclass
from types import MappingProxyType
from typing import FrozenSet

@dataclass(frozen=True)
class RuntimeExecutionContextMetadata:
    labels: MappingProxyType[str, str]
    annotations: MappingProxyType[str, str]
    tags: FrozenSet[str]
