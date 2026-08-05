"""
Dependency Traversal strategies.

Pure functional algorithms for traversing the graph.
"""

from typing import Dict, List, Set, Callable
from collections import deque
from .dependency_exceptions import TraversalException

class DependencyTraversal:
    """
    Strategy-oriented architecture for traversing dependency graphs.
    """

    @staticmethod
    def dfs(
        start_node: str,
        adjacency_map: Dict[str, List[str]],
        visitor: Callable[[str], None]
    ) -> None:
        """
        Deterministic Depth First Search.
        """
        visited = set()
        
        def _dfs(node: str):
            if node in visited:
                return
            visited.add(node)
            visitor(node)
            # Deterministic ordering
            for neighbor in sorted(adjacency_map.get(node, [])):
                _dfs(neighbor)
                
        _dfs(start_node)

    @staticmethod
    def bfs(
        start_node: str,
        adjacency_map: Dict[str, List[str]],
        visitor: Callable[[str], None]
    ) -> None:
        """
        Deterministic Breadth First Search.
        """
        visited = set([start_node])
        queue = deque([start_node])
        
        while queue:
            node = queue.popleft()
            visitor(node)
            
            # Deterministic ordering
            for neighbor in sorted(adjacency_map.get(node, [])):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

    @staticmethod
    def topological_sort(
        nodes: Set[str],
        adjacency_map: Dict[str, List[str]]
    ) -> List[str]:
        """
        Deterministic topological sort using Kahn's algorithm.
        Raises TraversalException if a cycle is detected (sort impossible).
        """
        in_degree_map = {node: 0 for node in nodes}
        for u in nodes:
            for v in adjacency_map.get(u, []):
                if v in in_degree_map:
                    in_degree_map[v] += 1

        # Use deterministic extraction (sort reversed, pop from end)
        available = sorted([n for n, d in in_degree_map.items() if d == 0], reverse=True)
        result_list = []

        while available:
            node = available.pop()
            result_list.append(node)

            # Deterministic ordering for neighbors
            for neighbor in sorted(adjacency_map.get(node, [])):
                if neighbor in in_degree_map:
                    in_degree_map[neighbor] -= 1
                    if in_degree_map[neighbor] == 0:
                        # Keep available sorted reversed to pop smallest element
                        available.append(neighbor)
                        available.sort(reverse=True)

        if len(result_list) != len(nodes):
            raise TraversalException("Graph contains cycles; topological sort failed.")

        return result_list
