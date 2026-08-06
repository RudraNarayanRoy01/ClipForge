from dataclasses import dataclass
from .runtime_execution_descriptor import RuntimeExecutionDescriptor
from .runtime_execution_metadata import RuntimeExecutionMetadata
from .runtime_execution_state import RuntimeExecutionState
from .runtime_execution_snapshot import RuntimeExecutionSnapshot

@dataclass(frozen=True)
class RuntimeExecutionIdentity:
    descriptor: RuntimeExecutionDescriptor
    metadata: RuntimeExecutionMetadata
    state: RuntimeExecutionState
    snapshot: RuntimeExecutionSnapshot
