from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionDescriptor:
    execution_id: str
    runtime_id: str
    bootstrap_id: str
    version: str
    schema_version: str
