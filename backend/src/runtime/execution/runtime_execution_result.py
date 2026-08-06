from dataclasses import dataclass
from .runtime_execution import RuntimeExecution
from .runtime_execution_snapshot import RuntimeExecutionSnapshot
from .runtime_execution_exceptions import RuntimeExecutionException

@dataclass(frozen=True)
class RuntimeExecutionResult:
    execution: RuntimeExecution
    snapshot: RuntimeExecutionSnapshot
    warnings: tuple[str, ...]
    errors: tuple[RuntimeExecutionException, ...]
