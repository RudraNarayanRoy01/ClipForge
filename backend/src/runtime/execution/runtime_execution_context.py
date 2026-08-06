from dataclasses import dataclass
from .runtime_execution_context_identity import RuntimeExecutionContextIdentity

@dataclass(frozen=True)
class RuntimeExecutionContext:
    identifier: str
    identity: RuntimeExecutionContextIdentity
