from dataclasses import dataclass
from .runtime_execution_lifecycle_identity import RuntimeExecutionLifecycleIdentity

@dataclass(frozen=True)
class RuntimeExecutionLifecycle:
    identifier: str
    identity: RuntimeExecutionLifecycleIdentity
