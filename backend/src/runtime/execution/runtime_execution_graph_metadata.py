from dataclasses import dataclass, field
from typing import FrozenSet

@dataclass(frozen=True)
class RuntimeExecutionGraphMetadata:
    labels: FrozenSet[str] = field(default_factory=frozenset)
    annotations: FrozenSet[str] = field(default_factory=frozenset)
    tags: FrozenSet[str] = field(default_factory=frozenset)
