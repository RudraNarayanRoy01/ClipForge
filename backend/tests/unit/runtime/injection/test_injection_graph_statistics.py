import pytest
from backend.src.runtime.injection.runtime_injection_graph_statistics import RuntimeInjectionGraphStatistics

def test_graph_statistics_immutability():
    stats = RuntimeInjectionGraphStatistics(
        edge_count=1,
        vertex_count=2,
        root_count=1,
        leaf_count=1,
        connected_components=1,
        graph_depth=2,
        graph_width=1,
        average_degree=1.0,
        maximum_degree=1,
        minimum_degree=1
    )
    with pytest.raises(Exception):
        stats.edge_count = 5

def test_graph_statistics_initialization():
    stats = RuntimeInjectionGraphStatistics(
        edge_count=10,
        vertex_count=20,
        root_count=5,
        leaf_count=5,
        connected_components=2,
        graph_depth=4,
        graph_width=3,
        average_degree=1.5,
        maximum_degree=3,
        minimum_degree=0
    )
    assert stats.edge_count == 10
    assert stats.vertex_count == 20
    assert stats.root_count == 5
    assert stats.connected_components == 2

def test_graph_statistics_read_only():
    stats = RuntimeInjectionGraphStatistics(0,0,0,0,0,0,0,0.0,0,0)
    with pytest.raises(AttributeError):
        del stats.root_count

def test_graph_statistics_equality():
    s1 = RuntimeInjectionGraphStatistics(1,2,1,1,1,2,1,1.0,1,1)
    s2 = RuntimeInjectionGraphStatistics(1,2,1,1,1,2,1,1.0,1,1)
    assert s1 == s2
