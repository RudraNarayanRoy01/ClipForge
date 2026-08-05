import pytest
from backend.src.runtime.composition.composition_validator import CompositionValidator
from backend.src.runtime.registry.component_registry import RuntimeComponentRegistry
from backend.src.runtime.dependency.dependency_graph import RuntimeDependencyGraph
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from backend.src.runtime.registry.component_types import RuntimeComponentType
from backend.src.runtime.registry.component_status import RuntimeComponentStatus
from backend.src.runtime.dependency.dependency_type import DependencyType
from backend.src.runtime.composition.composition_exceptions import (
    CompositionValidationException,
    IncompleteCompositionException
)

def test_validator_missing_registry():
    graph = RuntimeDependencyGraph()
    with pytest.raises(CompositionValidationException, match="RuntimeComponentRegistry is required."):
        CompositionValidator.validate(None, graph)

def test_validator_missing_graph():
    registry = RuntimeComponentRegistry()
    with pytest.raises(CompositionValidationException, match="RuntimeDependencyGraph is required."):
        CompositionValidator.validate(registry, None)

def test_validator_incomplete_composition():
    registry = RuntimeComponentRegistry()
    registry.register(RuntimeComponent("c1", "Comp1", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED))
    
    graph = RuntimeDependencyGraph()
    graph.register_node("c1")
    graph.register_node("c2") # c2 is not in registry
    
    with pytest.raises(IncompleteCompositionException, match="Graph references components not in registry"):
        CompositionValidator.validate(registry, graph)

def test_validator_invalid_graph():
    registry = RuntimeComponentRegistry()
    registry.register(RuntimeComponent("c1", "Comp1", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED))
    registry.register(RuntimeComponent("c2", "Comp2", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED))
    
    graph = RuntimeDependencyGraph()
    graph.register_node("c1")
    graph.register_node("c2")
    graph.register_dependency("c1", "c2", DependencyType.REQUIRED)
    graph.register_dependency("c2", "c1", DependencyType.REQUIRED) # cycle
    
    with pytest.raises(CompositionValidationException, match="Dependency graph is invalid"):
        CompositionValidator.validate(registry, graph)

def test_validator_success():
    registry = RuntimeComponentRegistry()
    registry.register(RuntimeComponent("c1", "Comp1", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED))
    
    graph = RuntimeDependencyGraph()
    graph.register_node("c1")
    
    warnings = CompositionValidator.validate(registry, graph)
    assert isinstance(warnings, list)
