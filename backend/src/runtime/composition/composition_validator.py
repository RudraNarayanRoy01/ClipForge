from typing import List, Optional
from backend.src.runtime.registry.component_registry import RuntimeComponentRegistry
from backend.src.runtime.dependency.dependency_graph import RuntimeDependencyGraph
from .composition_exceptions import CompositionValidationException, IncompleteCompositionException

class CompositionValidator:
    """
    Validator for Runtime Composition structures.
    
    Responsibilities:
    - Validate RuntimeComponentRegistry presence
    - Validate RuntimeDependencyGraph presence
    - Validate Registry completeness
    - Validate Dependency Graph validity
    - Validate Composition completeness
    - Validate ownership boundaries
    """
    
    @staticmethod
    def validate(registry: Optional[RuntimeComponentRegistry], graph: Optional[RuntimeDependencyGraph]) -> List[str]:
        """
        Performs all structural validations.
        Raises specific exceptions if validation fails.
        Returns a list of warnings if any non-fatal issues exist.
        """
        if registry is None:
            raise CompositionValidationException("RuntimeComponentRegistry is required.")
        if graph is None:
            raise CompositionValidationException("RuntimeDependencyGraph is required.")
            
        warnings: List[str] = []
        
        registry_snapshot = registry.get_snapshot()
        graph_snapshot = graph.create_snapshot()
        
        registry_component_ids = {comp.component_id for comp in registry_snapshot.components}
        graph_node_ids = frozenset(graph_snapshot.nodes)
        
        # Check completeness: Does graph contain nodes that don't exist in registry?
        missing_in_registry = graph_node_ids - registry_component_ids
        if missing_in_registry:
            error_msg = f"Graph references components not in registry: {missing_in_registry}"
            raise IncompleteCompositionException(error_msg)
            
        # Validate graph consistency
        if not graph_snapshot.validation_summary.success:
            error_msg = f"Dependency graph is invalid (cycles: {graph_snapshot.validation_summary.cycles_detected}, missing: {graph_snapshot.validation_summary.missing_components})"
            raise CompositionValidationException(error_msg)
            
        return warnings
