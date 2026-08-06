from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionVariable:
    identifier: str
    name: str
    variable_type: str
    required: bool
    default_reference: str
    description: str
