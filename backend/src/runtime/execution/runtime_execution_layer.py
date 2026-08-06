from dataclasses import dataclass
from typing import Tuple
from .runtime_execution_dependency_batch import RuntimeExecutionDependencyBatch

@dataclass(frozen=True)
class RuntimeExecutionLayer:
    layer_identifier: str
    batches: Tuple[RuntimeExecutionDependencyBatch, ...]
