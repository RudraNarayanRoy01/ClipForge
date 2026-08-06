from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionEngineDescriptor:
    execution_id: str
    runtime_id: str
    graph_id: str
    plan_id: str
    context_id: str
    composition_id: str
    builder_id: str
    lifecycle_id: str
    scheduler_id: str
    engine_id: str
    version: str
    schema_version: str
