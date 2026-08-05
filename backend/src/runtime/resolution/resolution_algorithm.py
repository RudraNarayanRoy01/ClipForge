from typing import Tuple, FrozenSet, Dict, List, Set
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from .resolution_exceptions import ResolutionCycleException, ResolutionOrderingException

class ResolutionAlgorithm:
    """
    Pure computational module for deterministic topological ordering.
    
    Responsibilities:
    - deterministic topological ordering
    - dependency ordering (layering)
    - ordering validation
    - stable ordering
    
    No Runtime mutation. No execution. No logging.
    """
    
    @staticmethod
    def compute_ordering(composition: 'RuntimeComposition') -> Tuple[Tuple[RuntimeComponent, ...], Tuple[FrozenSet[str], ...]]:
        """
        Computes deterministic topological ordering of components.
        
        Returns:
            Tuple containing:
            - Tuple of ordered RuntimeComponents
            - Tuple of FrozenSets representing independent layers of component IDs
        """
        components: Dict[str, RuntimeComponent] = {c.component_id: c for c in composition.components}
        
        # Build adjacency list (source -> target means source depends on target)
        # Wait, if A depends on B, B must be initialized first.
        # Dependency direction: source depends on target. 
        # So in_degree is the number of things this node depends on (out-edges in graph theory).
        # We want to process nodes with 0 dependencies first.
        
        # depends_on: node -> set of nodes it depends on
        depends_on: Dict[str, Set[str]] = {c_id: set() for c_id in components}
        # depended_by: node -> set of nodes that depend on it
        depended_by: Dict[str, Set[str]] = {c_id: set() for c_id in components}
        
        for dep in composition.dependencies:
            # Only consider internal dependencies that actually exist
            if dep.source_component_id in components and dep.target_component_id in components:
                depends_on[dep.source_component_id].add(dep.target_component_id)
                depended_by[dep.target_component_id].add(dep.source_component_id)
                
        layers: List[FrozenSet[str]] = []
        ordered_ids: List[str] = []
        
        remaining = set(components.keys())
        
        while remaining:
            # Find nodes with no unresolved dependencies
            ready_nodes = {node for node in remaining if not depends_on[node].intersection(remaining)}
            
            if not ready_nodes:
                raise ResolutionCycleException("Dependency cycle detected; cannot compute stable ordering.")
                
            # Deterministic sorting within the layer
            sorted_layer = sorted(list(ready_nodes))
            
            layers.append(frozenset(sorted_layer))
            ordered_ids.extend(sorted_layer)
            
            remaining -= ready_nodes
            
        ordered_components = tuple(components[c_id] for c_id in ordered_ids)
        dependency_order = tuple(layers)
        
        return ordered_components, dependency_order
