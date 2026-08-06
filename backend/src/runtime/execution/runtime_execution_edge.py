from dataclasses import dataclass

@dataclass(frozen=True)
class RuntimeExecutionEdge:
    edge_identifier: str
    source_node_identifier: str
    destination_node_identifier: str
    relationship_type: str
    metadata_reference: str
