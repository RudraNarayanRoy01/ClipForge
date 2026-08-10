from dataclasses import dataclass
from .runtime_execution_descriptor import RuntimeExecutionDescriptor
from .runtime_execution_metadata import RuntimeExecutionMetadata
from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus
from .runtime_execution_snapshot import RuntimeExecutionSnapshot

@dataclass(frozen=True)
class RuntimeExecutionIdentity:
    descriptor: RuntimeExecutionDescriptor
    metadata: RuntimeExecutionMetadata
    status: RuntimeExecutionStatus
    snapshot: RuntimeExecutionSnapshot
