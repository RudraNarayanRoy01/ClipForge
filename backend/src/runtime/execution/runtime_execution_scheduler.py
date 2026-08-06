from dataclasses import dataclass
from .runtime_execution_scheduler_identity import RuntimeExecutionSchedulerIdentity

@dataclass(frozen=True)
class RuntimeExecutionScheduler:
    identifier: str
    identity: RuntimeExecutionSchedulerIdentity
