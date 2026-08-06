from typing import Tuple, FrozenSet
from .runtime_execution_node import RuntimeExecutionNode
from .runtime_execution_edge import RuntimeExecutionEdge
from .runtime_execution_graph import RuntimeExecutionGraph
from .runtime_execution_graph_identity import RuntimeExecutionGraphIdentity
from .runtime_execution_graph_descriptor import RuntimeExecutionGraphDescriptor
from .runtime_execution_graph_metadata import RuntimeExecutionGraphMetadata
from .runtime_execution_graph_statistics import RuntimeExecutionGraphStatistics
from .runtime_execution_graph_snapshot import RuntimeExecutionGraphSnapshot

from .execution_graph_descriptor_factory import ExecutionGraphDescriptorFactory
from .execution_graph_metadata_factory import ExecutionGraphMetadataFactory
from .execution_graph_factory import ExecutionGraphFactory
from .execution_graph_statistics_builder import ExecutionGraphStatisticsBuilder
from .execution_graph_snapshot_factory import ExecutionGraphSnapshotFactory

class RuntimeExecutionGraphFactory:
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
    def build(
        nodes: Tuple[RuntimeExecutionNode, ...],
        edges: Tuple[RuntimeExecutionEdge, ...],
        labels: FrozenSet[str] = frozenset(),
        annotations: FrozenSet[str] = frozenset(),
        tags: FrozenSet[str] = frozenset()
    ) -> RuntimeExecutionGraph:
        descriptor = ExecutionGraphDescriptorFactory.create_descriptor()
        metadata = ExecutionGraphMetadataFactory.create_metadata(
            labels=labels,
            annotations=annotations,
            tags=tags
        )
        
        (
            node_lookup,
            edge_lookup,
            descriptor_lookup,
            incoming_lookup,
            outgoing_lookup,
            roots,
            leaves
        ) = ExecutionGraphFactory.build_lookups(nodes, edges)
        
        statistics = ExecutionGraphStatisticsBuilder.build(
            nodes=nodes,
            edges=edges,
            roots=roots,
            leaves=leaves,
            outgoing_lookup=outgoing_lookup
        )
        
        snapshot = ExecutionGraphSnapshotFactory.create_snapshot(
            descriptor=descriptor,
            nodes=nodes,
            edges=edges,
            metadata=metadata,
            statistics=statistics,
            node_lookup=node_lookup,
            edge_lookup=edge_lookup,
            incoming_lookup=incoming_lookup,
            outgoing_lookup=outgoing_lookup,
            descriptor_lookup=descriptor_lookup
        )
        
        identity = RuntimeExecutionGraphIdentity(
            descriptor=descriptor,
            metadata=metadata,
            statistics=statistics,
            snapshot=snapshot,
            nodes=nodes,
            edges=edges,
            node_lookup=node_lookup,
            edge_lookup=edge_lookup,
            descriptor_lookup=descriptor_lookup,
            incoming_lookup=incoming_lookup,
            outgoing_lookup=outgoing_lookup,
            roots=roots,
            leaves=leaves
        )
        
        return RuntimeExecutionGraph(
            identifier=descriptor.graph_id,
            identity=identity
        )
