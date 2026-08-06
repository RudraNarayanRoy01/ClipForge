from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionContextDescriptor:
    execution_id: str
    runtime_id: str
    graph_id: str
    plan_id: str
    context_id: str
    version: str
    schema_version: str
