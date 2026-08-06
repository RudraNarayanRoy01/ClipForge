from dataclasses import dataclass
from .runtime_execution_engine_identity import RuntimeExecutionEngineIdentity

@dataclass(frozen=True)
class RuntimeExecutionEngine:
    identifier: str
    identity: RuntimeExecutionEngineIdentity
