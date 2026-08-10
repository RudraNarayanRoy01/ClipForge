from dataclasses import dataclass
from .runtime_execution_dispatcher_identity import RuntimeExecutionDispatcherIdentity

@dataclass(frozen=True)
class RuntimeExecutionDispatcher:
    identifier: str
    identity: RuntimeExecutionDispatcherIdentity
