from dataclasses import dataclass
from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.core.execution_workload import ExecutionWorkload

@dataclass(frozen=True)
class ExecutionAdmission:
    """
    Immutable representation of the Runtime's execution admission boundary.

    This explicitly normalized executable workload has been paired with an
    explicitly routed execution target and is authorized to cross into the
    execution domain.
    """
    execution_target: ExecutionTarget
    execution_workload: ExecutionWorkload
