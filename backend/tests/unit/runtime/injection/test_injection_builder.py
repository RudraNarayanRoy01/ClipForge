import pytest
from backend.src.runtime.injection.runtime_injection_builder import RuntimeInjectionBuilder
from backend.src.runtime.injection.runtime_injection_binding import RuntimeInjectionBinding


def test_builder_success():
    builder = RuntimeInjectionBuilder()
    bindings = (
        RuntimeInjectionBinding("I1", "Impl1", "s1", "SINGLETON", "GLOBAL"),
    )
    adjacency = {}
    
    result = builder.build(bindings, adjacency)
    
    assert result.success is True
    assert result.composition is not None
    assert result.composition.graph.bindings == bindings
    assert result.composition.statistics.binding_count == 1
    assert result.composition.statistics.graph_statistics.vertex_count == 1

def test_builder_failure():
    builder = RuntimeInjectionBuilder()
    bindings = (
        RuntimeInjectionBinding("I1", "Impl1", "s1", "SINGLETON", "GLOBAL"),
        RuntimeInjectionBinding("I1", "Impl2", "s2", "SINGLETON", "GLOBAL"),
    )
    adjacency = {}
    
    result = builder.build(bindings, adjacency)
    
    assert result.success is False
    assert result.composition is None
    assert len(result.errors) > 0
    assert "Duplicate binding detected" in result.errors[0]

def test_builder_catches_unexpected_errors(monkeypatch):
    builder = RuntimeInjectionBuilder()
    
    # Force an unexpected error inside the orchestrator
    def mock_validate(*args, **kwargs):
        raise ValueError("Something catastrophic happened")
        
    monkeypatch.setattr(builder._validator, "validate_bindings", mock_validate)
    
    bindings = (RuntimeInjectionBinding("I1", "Impl1", "s1", "S", "G"),)
    result = builder.build(bindings, {})
    
    assert result.success is False
    assert result.composition is None
    assert "Unexpected error: Something catastrophic happened" in result.errors[0]
    
def test_builder_produces_complete_pipeline():
    builder = RuntimeInjectionBuilder()
    bindings = (RuntimeInjectionBinding("I1", "Impl1", "s1", "S", "G"),)
    
    result = builder.build(bindings, {})
    assert result.success is True
    comp = result.composition
    
    # Verify all artifacts are attached
    assert comp.composition_id is not None
    assert comp.graph is not None
    assert comp.metadata is not None
    assert comp.statistics is not None
    assert comp.snapshot is not None
