from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionNode:
    identifier: str
    descriptor_reference: str
    metadata_reference: str
