from dataclasses import dataclass
from .runtime_execution_identity import RuntimeExecutionIdentity

@dataclass(frozen=True)
class RuntimeExecution:
    identifier: str
    identity: RuntimeExecutionIdentity
