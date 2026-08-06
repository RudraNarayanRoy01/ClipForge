from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionPlanDescriptor:
    execution_id: str
    runtime_id: str
    graph_id: str
    plan_id: str
    version: str
    schema_version: str
