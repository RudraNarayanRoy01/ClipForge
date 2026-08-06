import hashlib
import json
from typing import Tuple, Mapping
from types import MappingProxyType
from .runtime_execution_node import RuntimeExecutionNode
from .runtime_execution_edge import RuntimeExecutionEdge
from .runtime_execution_graph_descriptor import RuntimeExecutionGraphDescriptor
from .runtime_execution_graph_metadata import RuntimeExecutionGraphMetadata
from .runtime_execution_graph_statistics import RuntimeExecutionGraphStatistics
from .runtime_execution_graph_snapshot import RuntimeExecutionGraphSnapshot

class ExecutionGraphSnapshotFactory:
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
    def _hash_string(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def _hash_dict(data: dict) -> str:
        return ExecutionGraphSnapshotFactory._hash_string(
            json.dumps(data, sort_keys=True)
        )

    @staticmethod
    def create_snapshot(
        descriptor: RuntimeExecutionGraphDescriptor,
        nodes: Tuple[RuntimeExecutionNode, ...],
        edges: Tuple[RuntimeExecutionEdge, ...],
        metadata: RuntimeExecutionGraphMetadata,
        statistics: RuntimeExecutionGraphStatistics,
        node_lookup: MappingProxyType,
        edge_lookup: MappingProxyType,
        incoming_lookup: MappingProxyType,
        outgoing_lookup: MappingProxyType,
        descriptor_lookup: MappingProxyType
    ) -> RuntimeExecutionGraphSnapshot:
        descriptor_dict = {
            "execution_id": descriptor.execution_id,
            "runtime_id": descriptor.runtime_id,
            "graph_id": descriptor.graph_id,
            "version": descriptor.version,
            "schema_version": descriptor.schema_version
        }
        descriptor_hash = ExecutionGraphSnapshotFactory._hash_dict(descriptor_dict)

        node_dicts = [
            {
                "identifier": n.identifier,
                "descriptor_reference": n.descriptor_reference,
                "metadata_reference": n.metadata_reference
            } for n in sorted(nodes, key=lambda x: x.identifier)
        ]
        node_hash = ExecutionGraphSnapshotFactory._hash_dict({"nodes": node_dicts})

        edge_dicts = [
            {
                "edge_identifier": e.edge_identifier,
                "source_node_identifier": e.source_node_identifier,
                "destination_node_identifier": e.destination_node_identifier,
                "relationship_type": e.relationship_type,
                "metadata_reference": e.metadata_reference
            } for e in sorted(edges, key=lambda x: x.edge_identifier)
        ]
        edge_hash = ExecutionGraphSnapshotFactory._hash_dict({"edges": edge_dicts})

        graph_hash = ExecutionGraphSnapshotFactory._hash_dict({
            "nodes_hash": node_hash,
            "edges_hash": edge_hash
        })
        
        lookup_dict = {
            "node_lookup_keys": sorted(list(node_lookup.keys())),
            "edge_lookup_keys": sorted(list(edge_lookup.keys())),
            "incoming_lookup": {k: sorted(list(v)) for k, v in incoming_lookup.items()},
            "outgoing_lookup": {k: sorted(list(v)) for k, v in outgoing_lookup.items()},
            "descriptor_lookup": {k: sorted(list(v)) for k, v in descriptor_lookup.items()}
        }
        lookup_hash = ExecutionGraphSnapshotFactory._hash_dict(lookup_dict)

        metadata_dict = {
            "labels": sorted(list(metadata.labels)),
            "annotations": sorted(list(metadata.annotations)),
            "tags": sorted(list(metadata.tags))
        }
        metadata_hash = ExecutionGraphSnapshotFactory._hash_dict(metadata_dict)

        stats_dict = {
            "node_count": statistics.node_count,
            "edge_count": statistics.edge_count,
            "root_count": statistics.root_count,
            "leaf_count": statistics.leaf_count,
            "graph_depth": statistics.graph_depth,
            "graph_width": statistics.graph_width,
            "connected_component_count": statistics.connected_component_count,
            "isolated_node_count": statistics.isolated_node_count
        }
        stats_hash = ExecutionGraphSnapshotFactory._hash_dict(stats_dict)

        snapshot_hash = ExecutionGraphSnapshotFactory._hash_dict({
            "descriptor_hash": descriptor_hash,
            "node_hash": node_hash,
            "edge_hash": edge_hash,
            "graph_hash": graph_hash,
            "lookup_hash": lookup_hash,
            "metadata_hash": metadata_hash,
            "statistics_hash": stats_hash
        })

        return RuntimeExecutionGraphSnapshot(
            descriptor_hash=descriptor_hash,
            node_hash=node_hash,
            edge_hash=edge_hash,
            graph_hash=graph_hash,
            lookup_hash=lookup_hash,
            metadata_hash=metadata_hash,
            graph_statistics_hash=stats_hash,
            snapshot_hash=snapshot_hash
        )
