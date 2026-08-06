from typing import Tuple, Mapping, FrozenSet
from types import MappingProxyType
from .runtime_execution_node import RuntimeExecutionNode
from .runtime_execution_edge import RuntimeExecutionEdge
from .runtime_execution_graph import RuntimeExecutionGraph
from .runtime_execution_graph_identity import RuntimeExecutionGraphIdentity
from .runtime_execution_graph_validator import RuntimeExecutionGraphValidator

class ExecutionGraphFactory:
    """
    Creates immutable metadata.
    
    Performs NO:
    - execution
    - scheduling
    - provider loading
    - lifecycle
    - dependency injection
    - orchestration
    - planning
    - monitoring
    - optimization
    """
    @staticmethod
    def build_lookups(
        nodes: Tuple[RuntimeExecutionNode, ...],
        edges: Tuple[RuntimeExecutionEdge, ...]
    ) -> Tuple[
        MappingProxyType,
        MappingProxyType,
        MappingProxyType,
        MappingProxyType,
        MappingProxyType,
        Tuple[str, ...],
        Tuple[str, ...]
    ]:
        RuntimeExecutionGraphValidator.validate(nodes, edges)

        outgoing_dict = {n.identifier: [] for n in nodes}
        incoming_dict = {n.identifier: [] for n in nodes}
        
        node_lookup_dict = {n.identifier: n for n in nodes}
        edge_lookup_dict = {e.edge_identifier: e for e in edges}
        descriptor_lookup_dict = {}
        
        for node in nodes:
            if node.descriptor_reference not in descriptor_lookup_dict:
                descriptor_lookup_dict[node.descriptor_reference] = []
            descriptor_lookup_dict[node.descriptor_reference].append(node.identifier)

        for edge in edges:
            outgoing_dict[edge.source_node_identifier].append(edge.destination_node_identifier)
            incoming_dict[edge.destination_node_identifier].append(edge.source_node_identifier)

        roots = tuple(sorted([n for n, deps in incoming_dict.items() if len(deps) == 0]))
        leaves = tuple(sorted([n for n, deps in outgoing_dict.items() if len(deps) == 0]))
        
        outgoing_lookup = MappingProxyType({k: tuple(sorted(v)) for k, v in outgoing_dict.items()})
        incoming_lookup = MappingProxyType({k: tuple(sorted(v)) for k, v in incoming_dict.items()})
        descriptor_lookup = MappingProxyType({k: tuple(sorted(v)) for k, v in descriptor_lookup_dict.items()})
        node_lookup = MappingProxyType(node_lookup_dict)
        edge_lookup = MappingProxyType(edge_lookup_dict)

        return (
            node_lookup,
            edge_lookup,
            descriptor_lookup,
            incoming_lookup,
            outgoing_lookup,
            roots,
            leaves
        )
