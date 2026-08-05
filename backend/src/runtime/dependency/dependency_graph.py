"""
Runtime Dependency Graph implementation.

The canonical graph structure managing components nodes and dependency edges.
Delegates validation to DependencyGraphValidator.
"""

import time
import uuid
from typing import Dict, List, Set, Optional
from .runtime_dependency import RuntimeDependency
from .dependency_type import DependencyType
from .dependency_snapshot import DependencySnapshot
from .dependency_statistics import DependencyStatistics
from .dependency_validation_result import DependencyValidationResult
from .dependency_graph_validator import DependencyGraphValidator
from .dependency_direction import DependencyDirection
from .dependency_exceptions import (
    DuplicateDependencyException,
    InvalidDependencyException,
    GraphFrozenException
)

class RuntimeDependencyGraph:
    """
    Manages the deterministic, immutable-friendly dependency relationships.
    """
    
    def __init__(self, graph_identifier: str = "default_runtime_graph"):
        self._graph_identifier = graph_identifier
        self._nodes: Set[str] = set()
        
        # edges keyed by dependency_id
        self._edges: Dict[str, RuntimeDependency] = {}
        
        # Adjacency lists for fast traversal.
        # Dict[source, List[target]]
        self._forward_adj: Dict[str, List[str]] = {}
        # Dict[target, List[source]]
        self._reverse_adj: Dict[str, List[str]] = {}
        
        self._frozen: bool = False
        self._version: int = 1
        self._created_at: float = time.time()

    @property
    def is_frozen(self) -> bool:
        """Returns True if the graph is frozen."""
        return self._frozen

    def register_node(self, component_id: str) -> None:
        """
        Registers a component node in the graph.
        """
        if self._frozen:
            raise GraphFrozenException("Cannot register node: Graph is frozen.")
        
        if component_id not in self._nodes:
            self._nodes.add(component_id)
            self._forward_adj[component_id] = []
            self._reverse_adj[component_id] = []
            self._version += 1

    def register_dependency(
        self,
        source_component_id: str,
        target_component_id: str,
        dependency_type: DependencyType,
        description: Optional[str] = None
    ) -> RuntimeDependency:
        """
        Registers a directed dependency from source to target.
        """
        if self._frozen:
            raise GraphFrozenException("Cannot register dependency: Graph is frozen.")
            
        if not source_component_id or not target_component_id:
            raise InvalidDependencyException("Source and target IDs must be provided.")
            
        if source_component_id == target_component_id:
            raise InvalidDependencyException(f"Component '{source_component_id}' cannot depend on itself.")
            
        # Ensure nodes exist
        self.register_node(source_component_id)
        self.register_node(target_component_id)
        
        # Check for duplicates
        for edge in self._edges.values():
            if (edge.source_component_id == source_component_id and 
                edge.target_component_id == target_component_id):
                raise DuplicateDependencyException(
                    f"Dependency from {source_component_id} to {target_component_id} already exists."
                )

        # Create immutable edge
        dep_id = str(uuid.uuid4())
        dependency = RuntimeDependency(
            dependency_id=dep_id,
            source_component_id=source_component_id,
            target_component_id=target_component_id,
            dependency_type=dependency_type,
            description=description
        )
        
        self._edges[dep_id] = dependency
        self._forward_adj[source_component_id].append(target_component_id)
        self._reverse_adj[target_component_id].append(source_component_id)
        
        self._version += 1
        return dependency

    def remove_dependency(self, dependency_id: str) -> None:
        """
        Removes a dependency by ID.
        """
        if self._frozen:
            raise GraphFrozenException("Cannot remove dependency: Graph is frozen.")
            
        if dependency_id in self._edges:
            edge = self._edges[dependency_id]
            self._forward_adj[edge.source_component_id].remove(edge.target_component_id)
            self._reverse_adj[edge.target_component_id].remove(edge.source_component_id)
            del self._edges[dependency_id]
            self._version += 1

    def freeze(self) -> None:
        """
        Permanently freezes the graph, preventing further modification.
        """
        self._frozen = True

    def get_dependencies(self, component_id: str) -> List[RuntimeDependency]:
        """
        Returns all dependencies FOR a given component (FORWARD direction).
        """
        return [
            edge for edge in self._edges.values()
            if edge.source_component_id == component_id
        ]

    def get_dependents(self, component_id: str) -> List[RuntimeDependency]:
        """
        Returns all components that depend ON a given component (REVERSE direction).
        """
        return [
            edge for edge in self._edges.values()
            if edge.target_component_id == component_id
        ]

    def enumerate_root_nodes(self) -> Set[str]:
        """
        Returns nodes with no dependencies (in-degree 0 in a reverse traversal, or 0 out-degree in forward).
        A root node is a component that does NOT depend on anything else.
        """
        return {
            node for node in self._nodes
            if len(self._forward_adj.get(node, [])) == 0
        }

    def enumerate_leaf_nodes(self) -> Set[str]:
        """
        Returns nodes that no other nodes depend upon.
        A leaf node is a component that nothing depends on.
        """
        return {
            node for node in self._nodes
            if len(self._reverse_adj.get(node, [])) == 0
        }

    def validate(self) -> DependencyValidationResult:
        """
        Delegates validation to the DependencyGraphValidator.
        """
        return DependencyGraphValidator.validate(
            nodes=self._nodes,
            edges=self._edges,
            adjacency_list=self._forward_adj,
            reverse_adjacency_list=self._reverse_adj
        )

    def generate_statistics(self) -> DependencyStatistics:
        """
        Generates immutable statistics for the graph.
        """
        node_count = len(self._nodes)
        edge_count = len(self._edges)
        roots = self.enumerate_root_nodes()
        leaves = self.enumerate_leaf_nodes()
        
        isolated = len(roots.intersection(leaves))
        
        req_count = sum(1 for e in self._edges.values() if e.dependency_type == DependencyType.REQUIRED)
        opt_count = sum(1 for e in self._edges.values() if e.dependency_type == DependencyType.OPTIONAL)
        
        avg_deps = edge_count / node_count if node_count > 0 else 0.0
        
        return DependencyStatistics(
            node_count=node_count,
            edge_count=edge_count,
            root_count=len(roots),
            leaf_count=len(leaves),
            isolated_node_count=isolated,
            required_dependency_count=req_count,
            optional_dependency_count=opt_count,
            average_dependencies=avg_deps,
            average_dependents=avg_deps
        )

    def create_snapshot(self) -> DependencySnapshot:
        """
        Creates an immutable point-in-time snapshot of the graph.
        """
        # Sort edges deterministically by source, then target for snapshot consistency
        sorted_edges = sorted(
            self._edges.values(),
            key=lambda e: (e.source_component_id, e.target_component_id)
        )
        
        return DependencySnapshot(
            graph_identifier=self._graph_identifier,
            graph_version=self._version,
            created_at=time.time(),
            frozen=self._frozen,
            nodes=frozenset(self._nodes),
            edges=tuple(sorted_edges),
            root_nodes=frozenset(self.enumerate_root_nodes()),
            leaf_nodes=frozenset(self.enumerate_leaf_nodes()),
            statistics=self.generate_statistics(),
            validation_summary=self.validate()
        )

    def get_adjacency_map(self, direction: DependencyDirection = DependencyDirection.FORWARD) -> Dict[str, List[str]]:
        """
        Returns a copy of the adjacency map for traversal purposes based on direction.
        """
        adj = self._forward_adj if direction == DependencyDirection.FORWARD else self._reverse_adj
        return {k: list(v) for k, v in adj.items()}
