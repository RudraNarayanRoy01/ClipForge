import pytest
from backend.src.runtime.dependency import (
    RuntimeDependencyGraph, 
    DependencyType,
    DuplicateDependencyException,
    InvalidDependencyException,
    GraphFrozenException,
    DependencyDirection
)

def test_graph_register_node():
    graph = RuntimeDependencyGraph()
    graph.register_node("comp_a")
    assert "comp_a" in graph._nodes

def test_graph_register_dependency():
    graph = RuntimeDependencyGraph()
    dep = graph.register_dependency("comp_a", "comp_b", DependencyType.REQUIRED)
    assert dep.source_component_id == "comp_a"
    assert dep.target_component_id == "comp_b"
    assert "comp_a" in graph._nodes
    assert "comp_b" in graph._nodes

def test_graph_duplicate_dependency():
    graph = RuntimeDependencyGraph()
    graph.register_dependency("comp_a", "comp_b", DependencyType.REQUIRED)
    with pytest.raises(DuplicateDependencyException):
        graph.register_dependency("comp_a", "comp_b", DependencyType.OPTIONAL)

def test_graph_self_dependency():
    graph = RuntimeDependencyGraph()
    with pytest.raises(InvalidDependencyException):
        graph.register_dependency("comp_a", "comp_a", DependencyType.REQUIRED)

def test_graph_frozen():
    graph = RuntimeDependencyGraph()
    graph.register_dependency("comp_a", "comp_b", DependencyType.REQUIRED)
    graph.freeze()
    
    assert graph.is_frozen
    with pytest.raises(GraphFrozenException):
        graph.register_dependency("comp_b", "comp_c", DependencyType.REQUIRED)
        
    with pytest.raises(GraphFrozenException):
        graph.register_node("comp_c")
        
    with pytest.raises(GraphFrozenException):
        deps = graph.get_dependencies("comp_a")
        graph.remove_dependency(deps[0].dependency_id)

def test_graph_get_dependencies():
    graph = RuntimeDependencyGraph()
    graph.register_dependency("A", "B", DependencyType.REQUIRED)
    graph.register_dependency("A", "C", DependencyType.OPTIONAL)
    
    deps = graph.get_dependencies("A")
    assert len(deps) == 2
    
    dependents = graph.get_dependents("B")
    assert len(dependents) == 1
    assert dependents[0].source_component_id == "A"

def test_graph_remove_dependency():
    graph = RuntimeDependencyGraph()
    dep = graph.register_dependency("A", "B", DependencyType.REQUIRED)
    graph.remove_dependency(dep.dependency_id)
    assert len(graph.get_dependencies("A")) == 0

def test_adjacency_map_directions():
    graph = RuntimeDependencyGraph()
    graph.register_dependency("A", "B", DependencyType.REQUIRED)
    
    fwd = graph.get_adjacency_map(DependencyDirection.FORWARD)
    assert fwd["A"] == ["B"]
    
    rev = graph.get_adjacency_map(DependencyDirection.REVERSE)
    assert rev["B"] == ["A"]
