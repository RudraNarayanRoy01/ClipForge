from dataclasses import dataclass
from typing import Tuple, FrozenSet

@dataclass(frozen=True)
class RuntimeExecutionDependencyBatch:
    batch_identifier: str
    ordered_node_identifiers: Tuple[str, ...]
    dependency_identifiers: FrozenSet[str]
