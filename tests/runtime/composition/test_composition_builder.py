import pytest
from backend.src.runtime.composition.composition_builder import RuntimeCompositionBuilder
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

def test_builder_successful_composition():
    registry = RuntimeComponentRegistry()
    comp1 = RuntimeComponent("c1", "Comp1", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED)
    comp2 = RuntimeComponent("c2", "Comp2", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED)
    registry.register(comp1)
    registry.register(comp2)
    
    graph = RuntimeDependencyGraph()
    graph.register_node("c1")
    graph.register_node("c2")
    graph.register_dependency("c1", "c2", DependencyType.REQUIRED)
    
    builder = RuntimeCompositionBuilder()
    result = builder.build(registry, graph)
    
    assert result.success is True
    assert result.composition is not None
    assert result.composition.statistics.component_count == 2
    assert result.composition.statistics.dependency_count == 1
    assert len(result.composition.components) == 2
    assert len(result.composition.dependencies) == 1

def test_builder_missing_registry():
    builder = RuntimeCompositionBuilder()
    graph = RuntimeDependencyGraph()
    
    with pytest.raises(CompositionValidationException, match="RuntimeComponentRegistry is required."):
        builder.build(None, graph)

def test_builder_missing_graph():
    builder = RuntimeCompositionBuilder()
    registry = RuntimeComponentRegistry()
    
    with pytest.raises(CompositionValidationException, match="RuntimeDependencyGraph is required."):
        builder.build(registry, None)

def test_builder_incomplete_composition():
    registry = RuntimeComponentRegistry()
    comp1 = RuntimeComponent("c1", "Comp1", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED)
    registry.register(comp1)
    
    graph = RuntimeDependencyGraph()
    graph.register_node("c1")
    graph.register_node("c2") # c2 is not in registry
    
    builder = RuntimeCompositionBuilder()
    with pytest.raises(IncompleteCompositionException, match="Graph references components not in registry"):
        builder.build(registry, graph)

def test_builder_deterministic_ordering():
    registry = RuntimeComponentRegistry()
    comp1 = RuntimeComponent("c1", "Comp1", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED)
    comp2 = RuntimeComponent("c2", "Comp2", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED)
    registry.register(comp1)
    registry.register(comp2)
    
    graph = RuntimeDependencyGraph()
    graph.register_node("c1")
    graph.register_node("c2")
    
    builder = RuntimeCompositionBuilder()
    result = builder.build(registry, graph)
    
    assert result.success is True
    assert result.composition.components[0].component_id == "c1"
    assert result.composition.components[1].component_id == "c2"

def test_builder_invalid_graph_consistency():
    registry = RuntimeComponentRegistry()
    comp1 = RuntimeComponent("c1", "Comp1", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED)
    registry.register(comp1)
    
    comp2 = RuntimeComponent("c2", "Comp2", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED)
    registry.register(comp2)
    
    graph = RuntimeDependencyGraph()
    graph.register_node("c1")
    graph.register_node("c2")
    graph.register_dependency("c1", "c2", DependencyType.REQUIRED)
    graph.register_dependency("c2", "c1", DependencyType.REQUIRED)
    
    builder = RuntimeCompositionBuilder()
    with pytest.raises(CompositionValidationException, match="Dependency graph is invalid"):
        builder.build(registry, graph)
