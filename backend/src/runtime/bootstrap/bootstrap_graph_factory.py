"""
Bootstrap Graph Factory.

Strict SRP factory for constructing the RuntimeBootstrapGraph topology.
Contains zero execution, planning, or ordering logic.
"""
from typing import Dict, Set, Tuple
from types import MappingProxyType

from .runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor
from .runtime_bootstrap_layer import RuntimeBootstrapLayer
from .runtime_bootstrap_graph import RuntimeBootstrapGraph


class BootstrapGraphFactory:
    """
    Factory dedicated exclusively to constructing the immutable RuntimeBootstrapGraph.
    """

    def build_graph(
        self,
        descriptors: Dict[str, RuntimeBootstrapDescriptor],
        layers: Dict[str, RuntimeBootstrapLayer],
        adjacency: Dict[str, Set[str]]
    ) -> RuntimeBootstrapGraph:
        """Constructs the canonical RuntimeBootstrapGraph."""
        
        # Calculate reverse adjacency
        reverse_adjacency: Dict[str, Set[str]] = {node_id: set() for node_id in descriptors}
        for node_id, deps in adjacency.items():
            for dep in deps:
                if dep in reverse_adjacency:
                    reverse_adjacency[dep].add(node_id)
        
        # Identify roots and leaves
        roots = {node for node, deps in adjacency.items() if not deps}
        leaves = {node for node, rev_deps in reverse_adjacency.items() if not rev_deps}
        
        # Build dependency lookup directly from adjacency
        dependency_lookup = {node: tuple(deps) for node, deps in adjacency.items()}
        
        return RuntimeBootstrapGraph(
            roots=frozenset(roots),
            leaves=frozenset(leaves),
            descriptor_lookup=MappingProxyType(descriptors),
            dependency_lookup=MappingProxyType(dependency_lookup),
            layer_lookup=MappingProxyType(layers),
            adjacency_lookup=MappingProxyType({k: tuple(v) for k, v in adjacency.items()}),
            reverse_adjacency_lookup=MappingProxyType({k: tuple(v) for k, v in reverse_adjacency.items()})
        )
