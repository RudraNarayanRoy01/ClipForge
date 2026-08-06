from dataclasses import dataclass
from .execution_stage import ExecutionStage

@dataclass(frozen=True)
class RuntimeExecutionState:
    stage: ExecutionStage
