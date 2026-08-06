from dataclasses import dataclass
from types import MappingProxyType

@dataclass(frozen=True)
class RuntimeExecutionPlanMetadata:
    labels: MappingProxyType[str, str]
    annotations: MappingProxyType[str, str]
    tags: MappingProxyType[str, str]
