from typing import Tuple, Mapping
from .runtime_execution_node import RuntimeExecutionNode
from .runtime_execution_edge import RuntimeExecutionEdge
from .runtime_execution_graph_statistics import RuntimeExecutionGraphStatistics

class ExecutionGraphStatisticsBuilder:
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
        roots: Tuple[str, ...],
        leaves: Tuple[str, ...],
        outgoing_lookup: Mapping[str, Tuple[str, ...]]
    ) -> RuntimeExecutionGraphStatistics:
        node_count = len(nodes)
        edge_count = len(edges)
        root_count = len(roots)
        leaf_count = len(leaves)
        
        node_ids = {node.identifier for node in nodes}
        visited = set()
        connected_component_count = 0
        isolated_node_count = 0
        
        undirected_adj = {nid: set() for nid in node_ids}
        for edge in edges:
            undirected_adj[edge.source_node_identifier].add(edge.destination_node_identifier)
            undirected_adj[edge.destination_node_identifier].add(edge.source_node_identifier)
            
        for nid in node_ids:
            if nid not in visited:
                connected_component_count += 1
                if not undirected_adj[nid]:
                    isolated_node_count += 1
                queue = [nid]
                while queue:
                    curr = queue.pop(0)
                    if curr not in visited:
                        visited.add(curr)
                        for neighbor in undirected_adj[curr]:
                            if neighbor not in visited:
                                queue.append(neighbor)
        
        graph_depth = 0
        memo = {}
        def get_depth(node_id: str, current_path: set) -> int:
            if node_id in current_path:
                return 0
            if node_id in memo:
                return memo[node_id]
            max_d = 0
            for neighbor in outgoing_lookup.get(node_id, ()):
                current_path.add(node_id)
                max_d = max(max_d, 1 + get_depth(neighbor, current_path))
                current_path.remove(node_id)
            memo[node_id] = max_d
            return max_d
            
        for root in roots:
            graph_depth = max(graph_depth, get_depth(root, set()))
            
        graph_width = 0
        if roots:
            level_queue = list(roots)
            level_visited = set(roots)
            while level_queue:
                graph_width = max(graph_width, len(level_queue))
                next_level = set()
                for n in level_queue:
                    for neighbor in outgoing_lookup.get(n, ()):
                        if neighbor not in level_visited:
                            level_visited.add(neighbor)
                            next_level.add(neighbor)
                level_queue = list(next_level)

        return RuntimeExecutionGraphStatistics(
            node_count=node_count,
            edge_count=edge_count,
            root_count=root_count,
            leaf_count=leaf_count,
            graph_depth=graph_depth,
            graph_width=graph_width,
            connected_component_count=connected_component_count,
            isolated_node_count=isolated_node_count
        )
