from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionBinding:
    identifier: str
    source_identifier: str
    target_identifier: str
    binding_type: str
    description: str
