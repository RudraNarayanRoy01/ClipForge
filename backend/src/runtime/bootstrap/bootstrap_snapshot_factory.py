"""
Bootstrap Snapshot Factory.

Strict SRP factory for constructing the RuntimeBootstrapSnapshot.
"""
import hashlib
import json
from typing import Any

from .runtime_bootstrap_graph import RuntimeBootstrapGraph
from .runtime_bootstrap_plan import RuntimeBootstrapPlan
from .runtime_bootstrap_metadata import RuntimeBootstrapMetadata
from .bootstrap_graph_statistics import BootstrapGraphStatistics
from .runtime_bootstrap_statistics import RuntimeBootstrapStatistics
from .runtime_bootstrap_snapshot import RuntimeBootstrapSnapshot


class BootstrapSnapshotFactory:
    """
    Factory dedicated exclusively to constructing the RuntimeBootstrapSnapshot.
    Contains deterministic SHA-256 generation logic.
    """

    def build_snapshot(
        self,
        graph: RuntimeBootstrapGraph,
        plan: RuntimeBootstrapPlan,
        metadata: RuntimeBootstrapMetadata,
        graph_statistics: BootstrapGraphStatistics,
        statistics: RuntimeBootstrapStatistics
    ) -> RuntimeBootstrapSnapshot:
        """Constructs canonical RuntimeBootstrapSnapshot."""
        
        # Helper for deterministic JSON hashing
        def _hash(obj: Any) -> str:
            serialized = json.dumps(obj, sort_keys=True)
            return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        graph_hash = self._hash_graph(graph, _hash)
        plan_hash = self._hash_plan(plan, _hash)
        metadata_hash = self._hash_metadata(metadata, _hash)
        graph_statistics_hash = self._hash_graph_stats(graph_statistics, _hash)
        statistics_hash = self._hash_stats(statistics, _hash)

        composition_hash = _hash({
            "graph": graph_hash,
            "plan": plan_hash,
            "metadata": metadata_hash,
            "graph_statistics": graph_statistics_hash,
            "statistics": statistics_hash
        })

        bootstrap_hash = _hash({
            "composition": composition_hash
        })

        return RuntimeBootstrapSnapshot(
            bootstrap_hash=bootstrap_hash,
            composition_hash=composition_hash,
            graph_hash=graph_hash,
            plan_hash=plan_hash,
            metadata_hash=metadata_hash,
            statistics_hash=statistics_hash,
            graph_statistics_hash=graph_statistics_hash
        )

    def _hash_graph(self, graph: RuntimeBootstrapGraph, hash_fn) -> str:
        return hash_fn({
            "roots": sorted(list(graph.roots)),
            "leaves": sorted(list(graph.leaves)),
            "adjacency": {k: sorted(list(v)) for k, v in graph.adjacency_lookup.items()}
        })

    def _hash_plan(self, plan: RuntimeBootstrapPlan, hash_fn) -> str:
        return hash_fn([layer.layer_identifier for layer in plan.layers])

    def _hash_metadata(self, metadata: RuntimeBootstrapMetadata, hash_fn) -> str:
        return hash_fn({
            "version": metadata.version,
            "schema": metadata.schema_version,
            "labels": dict(metadata.labels),
            "annotations": dict(metadata.annotations)
        })

    def _hash_graph_stats(self, stats: BootstrapGraphStatistics, hash_fn) -> str:
        return hash_fn({
            "nodes": stats.node_count,
            "edges": stats.edge_count,
            "roots": stats.root_count,
            "leaves": stats.leaf_count,
            "depth": stats.graph_depth,
            "width": stats.graph_width,
            "components": stats.connected_components
        })

    def _hash_stats(self, stats: RuntimeBootstrapStatistics, hash_fn) -> str:
        return hash_fn({
            "layer_count": stats.layer_count,
            "dependency_batch_count": stats.dependency_batch_count,
            "planned_initialization_steps": stats.planned_initialization_steps,
            "descriptor_count": stats.descriptor_count,
            "bootstrap_group_count": stats.bootstrap_group_count,
            "planning_depth": stats.planning_depth
        })
