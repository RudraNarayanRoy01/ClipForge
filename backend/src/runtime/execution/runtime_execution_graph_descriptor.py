from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionGraphDescriptor:
    execution_id: str
    runtime_id: str
    graph_id: str
    version: str
    schema_version: str
