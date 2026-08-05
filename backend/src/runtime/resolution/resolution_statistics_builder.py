from typing import Dict, Set
from .resolution_statistics import ResolutionStatistics
from backend.src.runtime.composition.runtime_composition import RuntimeComposition

class ResolutionStatisticsBuilder:
    """
    Computes observational statistics based on the topological structure of the dependency graph.
    """
    
    @staticmethod
    def build(composition: RuntimeComposition, layers: tuple) -> ResolutionStatistics:
        components = {c.component_id for c in composition.components}
        depends_on: Dict[str, Set[str]] = {c: set() for c in components}
        depended_by: Dict[str, Set[str]] = {c: set() for c in components}
        
        valid_dependencies = 0
        for dep in composition.dependencies:
            if dep.source_component_id in components and dep.target_component_id in components:
                depends_on[dep.source_component_id].add(dep.target_component_id)
                depended_by[dep.target_component_id].add(dep.source_component_id)
                valid_dependencies += 1
                
        root_nodes = sum(1 for c in components if not depends_on[c])
        leaf_nodes = sum(1 for c in components if not depended_by[c])
        
        # Calculate disconnected groups using BFS
        visited = set()
        disconnected_groups = 0
        
        for c in components:
            if c not in visited:
                disconnected_groups += 1
                queue = [c]
                visited.add(c)
                while queue:
                    curr = queue.pop(0)
                    neighbors = depends_on[curr].union(depended_by[curr])
                    for n in neighbors:
                        if n not in visited:
                            visited.add(n)
                            queue.append(n)
                            
        max_depth = len(layers) if layers else 0
        avg_depth = max_depth / 2.0 if max_depth > 0 else 0.0 # Simple approximation for observational stats
        
        return ResolutionStatistics(
            total_components=len(components),
            total_dependencies=valid_dependencies,
            root_nodes=root_nodes,
            leaf_nodes=leaf_nodes,
            disconnected_groups=disconnected_groups,
            maximum_dependency_depth=max_depth,
            average_dependency_depth=avg_depth
        )
