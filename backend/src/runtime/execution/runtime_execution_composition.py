from dataclasses import dataclass
from .runtime_execution_composition_identity import RuntimeExecutionCompositionIdentity

@dataclass(frozen=True)
class RuntimeExecutionComposition:
    identifier: str
    identity: RuntimeExecutionCompositionIdentity
