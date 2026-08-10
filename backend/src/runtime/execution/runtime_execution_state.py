from dataclasses import dataclass
from .runtime_execution_state_identity import RuntimeExecutionStateIdentity

@dataclass(frozen=True)
class RuntimeExecutionState:
    identifier: str
    identity: RuntimeExecutionStateIdentity
