from dataclasses import dataclass
from .runtime_execution_graph_identity import RuntimeExecutionGraphIdentity

@dataclass(frozen=True)
class RuntimeExecutionGraph:
    identifier: str
    identity: RuntimeExecutionGraphIdentity
