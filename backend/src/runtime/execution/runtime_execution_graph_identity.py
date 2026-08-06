from dataclasses import dataclass
from typing import Tuple, Mapping

from .runtime_execution_node import RuntimeExecutionNode
from .runtime_execution_edge import RuntimeExecutionEdge
from .runtime_execution_graph_descriptor import RuntimeExecutionGraphDescriptor
from .runtime_execution_graph_metadata import RuntimeExecutionGraphMetadata
from .runtime_execution_graph_statistics import RuntimeExecutionGraphStatistics
from .runtime_execution_graph_snapshot import RuntimeExecutionGraphSnapshot

@dataclass(frozen=True)
class RuntimeExecutionGraphIdentity:
    descriptor: RuntimeExecutionGraphDescriptor
    metadata: RuntimeExecutionGraphMetadata
    statistics: RuntimeExecutionGraphStatistics
    snapshot: RuntimeExecutionGraphSnapshot
    nodes: Tuple[RuntimeExecutionNode, ...]
    edges: Tuple[RuntimeExecutionEdge, ...]
    node_lookup: Mapping[str, RuntimeExecutionNode]
    edge_lookup: Mapping[str, RuntimeExecutionEdge]
    descriptor_lookup: Mapping[str, Tuple[str, ...]]
    incoming_lookup: Mapping[str, Tuple[str, ...]]
    outgoing_lookup: Mapping[str, Tuple[str, ...]]
    roots: Tuple[str, ...]
    leaves: Tuple[str, ...]
