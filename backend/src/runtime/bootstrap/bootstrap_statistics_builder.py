"""
Bootstrap Statistics Builder.

Strict SRP builder for computing Runtime Bootstrap statistics.
Produces TWO independent immutable artifacts.
"""
from typing import Tuple, Dict, Set

from .runtime_bootstrap_graph import RuntimeBootstrapGraph
from .runtime_bootstrap_plan import RuntimeBootstrapPlan
from .bootstrap_graph_statistics import BootstrapGraphStatistics
from .runtime_bootstrap_statistics import RuntimeBootstrapStatistics


class BootstrapStatisticsBuilder:
    """
    Builder dedicated exclusively to computing structural and planning statistics.
    """

    def build_statistics(
        self,
        graph: RuntimeBootstrapGraph,
        plan: RuntimeBootstrapPlan
    ) -> Tuple[BootstrapGraphStatistics, RuntimeBootstrapStatistics]:
        """
        Builds graph topology metrics and bootstrap planning metrics.
        Returns two independent artifacts.
        """
        graph_stats = self._build_graph_statistics(graph)
        plan_stats = self._build_plan_statistics(plan, graph)
        return graph_stats, plan_stats

    def _build_graph_statistics(self, graph: RuntimeBootstrapGraph) -> BootstrapGraphStatistics:
        adjacency = graph.adjacency_lookup

        node_count = len(graph.descriptor_lookup)
        edge_count = sum(len(deps) for deps in adjacency.values())
        root_count = len(graph.roots)
        leaf_count = len(graph.leaves)
        
        # Calculate graph depth (longest path)
        depth = self._calculate_max_depth(adjacency, graph.roots)
        
        # Calculate graph width (max independent nodes)
        width = self._calculate_max_width(adjacency, graph.roots)
        
        # connected components
        components = self._calculate_connected_components(adjacency)

        return BootstrapGraphStatistics(
            node_count=node_count,
            edge_count=edge_count,
            root_count=root_count,
            leaf_count=leaf_count,
            graph_depth=depth,
            graph_width=width,
            connected_components=components
        )

    def _build_plan_statistics(self, plan: RuntimeBootstrapPlan, graph: RuntimeBootstrapGraph) -> RuntimeBootstrapStatistics:
        layer_count = len(plan.layers)
        dependency_batch_count = sum(len(layer.dependency_batches) for layer in plan.layers)
        planned_initialization_steps = sum(len(batch.descriptors) for layer in plan.layers for batch in layer.dependency_batches)
        descriptor_count = len(graph.descriptor_lookup)
        bootstrap_group_count = dependency_batch_count # Same as batches conceptually in this layer
        planning_depth = layer_count # Depth is strictly the number of layers

        return RuntimeBootstrapStatistics(
            layer_count=layer_count,
            dependency_batch_count=dependency_batch_count,
            planned_initialization_steps=planned_initialization_steps,
            descriptor_count=descriptor_count,
            bootstrap_group_count=bootstrap_group_count,
            planning_depth=planning_depth
        )

    def _calculate_max_depth(self, adjacency: Dict[str, Tuple[str, ...]], roots: Set[str]) -> int:
        if not roots:
            return 0
            
        memo = {}

        def _dfs(node: str) -> int:
            if node in memo:
                return memo[node]
            
            deps = adjacency.get(node, ())
            if not deps:
                memo[node] = 1
                return 1
                
            max_child_depth = max((_dfs(dep) for dep in deps), default=0)
            memo[node] = max_child_depth + 1
            return memo[node]
            
        return max((_dfs(root) for root in roots), default=0)

    def _calculate_max_width(self, adjacency: Dict[str, Tuple[str, ...]], roots: Set[str]) -> int:
        if not roots:
            return 0
            
        # Simplified width calculation: max nodes at any depth level
        levels = {}
        
        def _bfs(nodes: Set[str], current_level: int):
            if not nodes:
                return
            levels[current_level] = levels.get(current_level, set()).union(nodes)
            next_level = set()
            for node in nodes:
                next_level.update(adjacency.get(node, ()))
            _bfs(next_level, current_level + 1)
            
        _bfs(roots, 0)
        
        return max(len(level_nodes) for level_nodes in levels.values())

    def _calculate_connected_components(self, adjacency: Dict[str, Tuple[str, ...]]) -> int:
        if not adjacency:
            return 0
            
        visited = set()
        components = 0
        
        # Build undirected graph
        undirected = {node: set(deps) for node, deps in adjacency.items()}
        for node, deps in adjacency.items():
            for dep in deps:
                if dep not in undirected:
                    undirected[dep] = set()
                undirected[dep].add(node)
                
        def _dfs(node: str):
            stack = [node]
            while stack:
                curr = stack.pop()
                if curr not in visited:
                    visited.add(curr)
                    stack.extend(undirected.get(curr, set()) - visited)
                    
        for node in adjacency.keys():
            if node not in visited:
                components += 1
                _dfs(node)
                
        return components
