from dataclasses import dataclass
from .runtime_execution_builder_identity import RuntimeExecutionBuilderIdentity

@dataclass(frozen=True)
class RuntimeExecutionBuilder:
    identifier: str
    identity: RuntimeExecutionBuilderIdentity
