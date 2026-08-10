from dataclasses import dataclass
from types import MappingProxyType

@dataclass(frozen=True)
class RuntimeExecutionDispatcherMetadata:
    labels: MappingProxyType[str, str]
    annotations: MappingProxyType[str, str]
    tags: frozenset[str]
