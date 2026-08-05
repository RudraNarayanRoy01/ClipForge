import pytest
from backend.src.runtime.injection.injection_statistics import InjectionStatistics
from backend.src.runtime.injection.runtime_injection_graph_statistics import RuntimeInjectionGraphStatistics


def test_statistics_immutability():
    g_stats = RuntimeInjectionGraphStatistics(0,0,0,0,0,0,0,0.0,0,0)
    stats = InjectionStatistics(
        binding_count=1,
        interface_count=1,
        implementation_count=1,
        singleton_bindings=1,
        transient_bindings=0,
        scoped_bindings=0,
        optional_dependency_count=0,
        required_dependency_count=0,
        graph_statistics=g_stats
    )
    with pytest.raises(Exception):
        stats.binding_count = 2

def test_statistics_initialization():
    g_stats = RuntimeInjectionGraphStatistics(10,20,5,5,2,4,3,1.5,3,0)
    stats = InjectionStatistics(
        binding_count=10,
        interface_count=8,
        implementation_count=10,
        singleton_bindings=5,
        transient_bindings=3,
        scoped_bindings=2,
        optional_dependency_count=3,
        required_dependency_count=12,
        graph_statistics=g_stats
    )
    assert stats.binding_count == 10
    assert stats.singleton_bindings == 5
    assert stats.graph_statistics.edge_count == 10
    assert stats.graph_statistics.graph_depth == 4
