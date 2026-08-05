"""
Runtime Bootstrap Validator.

Strict SRP validator for ensuring structural integrity of the Bootstrap foundation.
"""
from typing import Dict, Set, List
from .runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor
from .runtime_bootstrap_layer import RuntimeBootstrapLayer
from .bootstrap_exceptions import BootstrapValidationException


class RuntimeBootstrapValidator:
    """
    Validator exclusively responsible for ensuring structural integrity.
    Does not execute, schedule, or resolve dependencies.
    """

    def validate_inputs(
        self,
        descriptor: RuntimeBootstrapDescriptor,
        descriptors: Dict[str, RuntimeBootstrapDescriptor],
        layers: List[RuntimeBootstrapLayer],
        adjacency: Dict[str, Set[str]]
    ) -> None:
        """Validates all inputs before Bootstrap composition."""
        
        if not descriptor:
            raise BootstrapValidationException("Primary RuntimeBootstrapDescriptor is required.")
            
        if not descriptors:
            raise BootstrapValidationException("At least one RuntimeBootstrapDescriptor is required for composition.")
            
        if not layers:
            raise BootstrapValidationException("At least one RuntimeBootstrapLayer is required.")
            
        # Validate that all nodes in adjacency exist in descriptors
        for node, deps in adjacency.items():
            if node not in descriptors:
                raise BootstrapValidationException(f"Node '{node}' in adjacency list not found in descriptors.")
            for dep in deps:
                if dep not in descriptors:
                    raise BootstrapValidationException(f"Dependency '{dep}' of node '{node}' not found in descriptors.")
                    
        # Validate that layers only contain known descriptors
        for layer in layers:
            for batch in layer.dependency_batches:
                for desc in batch.descriptors:
                    if desc.identifier not in descriptors:
                        raise BootstrapValidationException(f"Descriptor '{desc.identifier}' in batch '{batch.batch_identifier}' not found in provided descriptors.")
                        
        # Basic cycle detection
        self._detect_cycles(adjacency)

    def _detect_cycles(self, adjacency: Dict[str, Set[str]]) -> None:
        visited = set()
        path = set()

        def _visit(node: str):
            if node in path:
                raise BootstrapValidationException(f"Cycle detected involving node '{node}'.")
            if node in visited:
                return
                
            path.add(node)
            for neighbor in adjacency.get(node, set()):
                _visit(neighbor)
            path.remove(node)
            visited.add(node)

        for node in adjacency:
            _visit(node)
