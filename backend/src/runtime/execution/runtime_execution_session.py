from dataclasses import dataclass
from .runtime_execution_session_identity import RuntimeExecutionSessionIdentity

@dataclass(frozen=True)
class RuntimeExecutionSession:
    identifier: str
    identity: RuntimeExecutionSessionIdentity
