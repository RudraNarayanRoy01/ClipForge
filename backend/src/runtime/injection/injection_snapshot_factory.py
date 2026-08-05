"""
Injection Snapshot Factory.

Creates immutable snapshots of the Runtime Injection Foundation.
Computes deterministic structural hashes.
"""
import hashlib
import json

from .injection_metadata import InjectionMetadata
from .injection_snapshot import InjectionSnapshot
from .injection_statistics import InjectionStatistics
from .runtime_injection_graph import RuntimeInjectionGraph


class InjectionSnapshotFactory:
    """
    Factory specifically for generating injection snapshots and calculating their deterministic hashes.
    """

    def create(
        self,
        composition_id: str,
        graph: RuntimeInjectionGraph,
        metadata: InjectionMetadata,
        statistics: InjectionStatistics
    ) -> InjectionSnapshot:
        """
        Creates a new immutable snapshot with calculated deterministic hashes.
        """
        binding_hash = self._calculate_binding_hash(graph)
        graph_hash = self._calculate_graph_hash(graph)
        metadata_hash = self._calculate_metadata_hash(metadata)

        return InjectionSnapshot(
            composition_id=composition_id,
            graph=graph,
            metadata=metadata,
            statistics=statistics,
            binding_hash=binding_hash,
            graph_hash=graph_hash,
            metadata_hash=metadata_hash
        )

    def _calculate_binding_hash(self, graph: RuntimeInjectionGraph) -> str:
        # Sort identifiers to be deterministic
        bindings = sorted([
            f"{b.interface_id}:{b.implementation_id}:{b.service_id}:{b.lifetime}:{b.scope}"
            for b in graph.bindings
        ])
        content = "|".join(bindings)
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _calculate_graph_hash(self, graph: RuntimeInjectionGraph) -> str:
        # Hash deterministic topology
        edges = []
        for src, descriptors in graph.adjacency.items():
            for desc in descriptors:
                edges.append(f"{src}->{desc.dependency_service}({desc.dependency_type})")
        
        edges.sort()
        content = "|".join(edges)
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _calculate_metadata_hash(self, metadata: InjectionMetadata) -> str:
        # Sort metadata keys
        sorted_keys = sorted(metadata.metadata_mapping.keys())
        metadata_str = "|".join(f"{k}:{metadata.metadata_mapping[k]}" for k in sorted_keys)
        content = f"{metadata.schema_version}|{metadata.builder_version}|{metadata_str}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
