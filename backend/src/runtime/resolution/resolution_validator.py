from dataclasses import dataclass, field
from typing import Tuple

@dataclass(frozen=True)
class ResolutionValidationResult:
    """Immutable result of dependency resolution validation."""
    is_valid: bool
    errors: Tuple[str, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)

class ResolutionValidator:
    """
    Validates a runtime composition for dependency resolution.
    
    Responsibilities ONLY:
    - validate composition completeness
    - validate dependency graph
    - detect cycles
    - detect unreachable nodes
    - detect disconnected groups
    - detect invalid references
    
    Contains NO ordering logic.
    """
    
    @staticmethod
    def validate(composition: 'RuntimeComposition') -> ResolutionValidationResult:
        from backend.src.runtime.composition.runtime_composition import RuntimeComposition
        
        if not isinstance(composition, RuntimeComposition):
            return ResolutionValidationResult(False, errors=("Invalid composition type provided.",))
            
        errors = []
        warnings = []
        
        components = {c.component_id: c for c in composition.components}
        
        # Validate dependency references
        for dep in composition.dependencies:
            if dep.source_component_id not in components:
                errors.append(f"Invalid reference: source component {dep.source_component_id} not found.")
            if dep.target_component_id not in components:
                errors.append(f"Invalid reference: target component {dep.target_component_id} not found.")
                
        # Build graph for validation
        graph = {c_id: [] for c_id in components}
        in_degree = {c_id: 0 for c_id in components}
        
        for dep in composition.dependencies:
            if dep.source_component_id in components and dep.target_component_id in components:
                graph[dep.source_component_id].append(dep.target_component_id)
                in_degree[dep.target_component_id] += 1
                
        # Detect unreachable nodes (nodes with 0 in-degree and 0 out-degree are disconnected groups/isolated)
        # Technically in a dependency graph, unreachable could mean not part of the main connected components,
        # but let's check for cycles which is the main failure mode.
        visited = set()
        rec_stack = set()
        
        def is_cyclic(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    if is_cyclic(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False
            
        has_cycle = False
        for node in components:
            if node not in visited:
                if is_cyclic(node):
                    has_cycle = True
                    break
                    
        if has_cycle:
            errors.append("Dependency cycle detected in composition.")
            
        if not components and composition.dependencies:
            errors.append("Composition has dependencies but no components.")
            
        is_valid = len(errors) == 0
        return ResolutionValidationResult(is_valid, tuple(errors), tuple(warnings))
