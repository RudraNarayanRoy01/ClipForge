from dataclasses import dataclass
from .runtime_execution_plan_identity import RuntimeExecutionPlanIdentity

@dataclass(frozen=True)
class RuntimeExecutionPlan:
    identifier: str
    identity: RuntimeExecutionPlanIdentity
