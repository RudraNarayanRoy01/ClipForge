import pytest
from backend.src.runtime.composition.composition_builder import RuntimeCompositionBuilder
from backend.src.runtime.registry.component_registry import RuntimeComponentRegistry
from backend.src.runtime.dependency.dependency_graph import RuntimeDependencyGraph
from backend.src.runtime.composition.composition_exceptions import CompositionBuildException

def test_builder_empty_registry_and_graph():
    registry = RuntimeComponentRegistry()
    graph = RuntimeDependencyGraph()
    
    builder = RuntimeCompositionBuilder()
    result = builder.build(registry, graph)
    
    assert result.success is True
    assert result.composition is not None
    assert result.composition.statistics.component_count == 0
    assert result.composition.statistics.dependency_count == 0
    assert len(result.composition.components) == 0
    assert len(result.composition.dependencies) == 0

def test_builder_sequential_builds():
    registry = RuntimeComponentRegistry()
    graph = RuntimeDependencyGraph()
    
    builder = RuntimeCompositionBuilder()
    result1 = builder.build(registry, graph)
    result2 = builder.build(registry, graph)
    
    assert result1.success is True
    assert result2.success is True
    assert result1.composition.composition_id != result2.composition.composition_id

def test_composition_result_immutability():
    registry = RuntimeComponentRegistry()
    graph = RuntimeDependencyGraph()
    builder = RuntimeCompositionBuilder()
    result = builder.build(registry, graph)
    
    import dataclasses
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.success = False

def test_warnings_and_errors_immutability():
    registry = RuntimeComponentRegistry()
    graph = RuntimeDependencyGraph()
    builder = RuntimeCompositionBuilder()
    result = builder.build(registry, graph)
    
    assert isinstance(result.warnings, tuple)
    assert isinstance(result.errors, tuple)

def test_builder_unexpected_exception_wraps_in_build_exception(monkeypatch):
    registry = RuntimeComponentRegistry()
    graph = RuntimeDependencyGraph()
    
    def fake_generate_id():
        raise RuntimeError("Unexpected error")
        
    from backend.src.runtime.composition.composition_id_factory import CompositionIdFactory
    monkeypatch.setattr(CompositionIdFactory, "generate_id", fake_generate_id)
    
    builder = RuntimeCompositionBuilder()
    
    with pytest.raises(CompositionBuildException, match="Failed to build composition: Unexpected error"):
        builder.build(registry, graph)
