from typing import Tuple
from .runtime_execution_node import RuntimeExecutionNode
from .runtime_execution_edge import RuntimeExecutionEdge
from .runtime_execution_exceptions import ExecutionValidationException

class RuntimeExecutionGraphValidator:
    """
    Validates structural integrity.
    
    Validates ONLY:
    - duplicate nodes
    - duplicate edges
    - missing nodes
    - broken references
    - lookup consistency
    - structural integrity
    
    DOES NOT validate:
    - execution ordering
    - execution correctness
    - execution plans
    - execution success
    - scheduling
    - providers
    - hardware
    - lifecycle
    - monitoring
    - telemetry
    - optimization
    - dependency injection
    """
    @staticmethod
    def validate(
        nodes: Tuple[RuntimeExecutionNode, ...],
        edges: Tuple[RuntimeExecutionEdge, ...]
    ) -> None:
        node_ids = set()
        for node in nodes:
            if node.identifier in node_ids:
                raise ExecutionValidationException(f"Duplicate node identifier: {node.identifier}")
            node_ids.add(node.identifier)

        edge_ids = set()
        for edge in edges:
            if edge.edge_identifier in edge_ids:
                raise ExecutionValidationException(f"Duplicate edge identifier: {edge.edge_identifier}")
            edge_ids.add(edge.edge_identifier)
            
            if edge.source_node_identifier not in node_ids:
                raise ExecutionValidationException(f"Broken edge: source node {edge.source_node_identifier} not found")
            if edge.destination_node_identifier not in node_ids:
                raise ExecutionValidationException(f"Broken edge: destination node {edge.destination_node_identifier} not found")
