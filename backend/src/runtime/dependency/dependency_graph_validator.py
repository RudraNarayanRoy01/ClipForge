"""
Dependency Graph Validator.

Responsible for orchestrating validation logic: cycle detection, missing components,
orphan nodes, and structural consistency without modifying the graph.
"""

import time
from typing import Dict, List, Set, Tuple, FrozenSet
from .runtime_dependency import RuntimeDependency
from .dependency_validation_result import DependencyValidationResult

class DependencyGraphValidator:
    """
    Validation orchestrator for the Dependency Graph.
    """

    @classmethod
    def validate(
        cls,
        nodes: Set[str],
        edges: Dict[str, RuntimeDependency],
        adjacency_list: Dict[str, List[str]],
        reverse_adjacency_list: Dict[str, List[str]]
    ) -> DependencyValidationResult:
        """
        Performs a full validation pass over the provided graph structures.
        """
        cycles = cls._detect_cycles(nodes, adjacency_list)
        missing = cls._detect_missing_components(nodes, edges)
        orphans = cls._detect_orphans(nodes, adjacency_list, reverse_adjacency_list)
        
        success = len(cycles) == 0 and len(missing) == 0
        
        warnings = []
        if orphans:
            warnings.append(f"Found {len(orphans)} orphan nodes.")

        return DependencyValidationResult(
            success=success,
            cycles_detected=tuple(tuple(c) for c in cycles),
            missing_components=frozenset(missing),
            orphan_nodes=frozenset(orphans),
            warnings=tuple(warnings),
            validation_timestamp=time.time()
        )

    @staticmethod
    def _detect_cycles(nodes: Set[str], adjacency_list: Dict[str, List[str]]) -> List[List[str]]:
        """
        Detects cycles in the directed graph using DFS.
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in adjacency_list.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Cycle found
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                    return True

            rec_stack.remove(node)
            path.pop()
            return False

        # Ensure deterministic traversal by sorting nodes
        for node in sorted(nodes):
            if node not in visited:
                dfs(node)
                
        return cycles

    @staticmethod
    def _detect_missing_components(nodes: Set[str], edges: Dict[str, RuntimeDependency]) -> Set[str]:
        """
        Identifies dependencies that reference target components not present in the nodes set.
        """
        missing = set()
        for edge in edges.values():
            if edge.target_component_id not in nodes:
                missing.add(edge.target_component_id)
        return missing

    @staticmethod
    def _detect_orphans(
        nodes: Set[str], 
        adjacency_list: Dict[str, List[str]], 
        reverse_adjacency_list: Dict[str, List[str]]
    ) -> Set[str]:
        """
        Identifies components that have no dependencies and are not depended upon by anything.
        """
        orphans = set()
        for node in nodes:
            has_deps = len(adjacency_list.get(node, [])) > 0
            is_dep = len(reverse_adjacency_list.get(node, [])) > 0
            if not has_deps and not is_dep:
                orphans.add(node)
        return orphans
