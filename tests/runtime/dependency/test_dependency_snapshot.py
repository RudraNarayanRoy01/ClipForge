import pytest
from dataclasses import FrozenInstanceError
from backend.src.runtime.dependency import (
    RuntimeDependencyGraph, 
    DependencyType
)

def test_snapshot_creation():
    graph = RuntimeDependencyGraph("test_graph")
    graph.register_dependency("A", "B", DependencyType.REQUIRED)
    
    snapshot = graph.create_snapshot()
    
    assert snapshot.graph_identifier == "test_graph"
    assert snapshot.graph_version == 3  # node A, node B, edge A->B
    assert not snapshot.frozen
    assert "A" in snapshot.nodes
    assert len(snapshot.edges) == 1

def test_snapshot_immutability():
    graph = RuntimeDependencyGraph()
    graph.register_dependency("A", "B", DependencyType.REQUIRED)
    snapshot = graph.create_snapshot()
    
    # Frozen classes cannot be modified
    with pytest.raises(FrozenInstanceError):
        snapshot.graph_version = 100
        
    # Check frozensets
    with pytest.raises(AttributeError):
        snapshot.nodes.add("C")

def test_statistics_generation():
    graph = RuntimeDependencyGraph()
    graph.register_node("Isolated")
    graph.register_dependency("A", "B", DependencyType.REQUIRED)
    graph.register_dependency("B", "C", DependencyType.OPTIONAL)
    
    stats = graph.generate_statistics()
    
    assert stats.node_count == 4
    assert stats.edge_count == 2
    assert stats.isolated_node_count == 1
    assert stats.required_dependency_count == 1
    assert stats.optional_dependency_count == 1
