import pytest
from backend.src.runtime.injection.injection_statistics_builder import InjectionStatisticsBuilder
from backend.src.runtime.injection.runtime_injection_binding import RuntimeInjectionBinding
from backend.src.runtime.injection.injection_descriptor import InjectionDescriptor


def test_statistics_builder_computes_correctly():
    builder = InjectionStatisticsBuilder()
    
    bindings = (
        RuntimeInjectionBinding("I1", "Impl1", "s1", "SINGLETON", "GLOBAL"),
        RuntimeInjectionBinding("I2", "Impl2", "s2", "TRANSIENT", "LOCAL"),
        RuntimeInjectionBinding("I3", "Impl3", "s3", "SCOPED", "REQ"),
        RuntimeInjectionBinding("I4", "Impl4", "s4", "SINGLETON", "GLOBAL"),
    )
    
    adjacency = {
        "I1": (
            InjectionDescriptor("REQ", False, "CTOR", "G", "I1", "I2"),
            InjectionDescriptor("REQ", True, "PROP", "G", "I1", "I3")
        ),
        "I2": (
            InjectionDescriptor("REQ", False, "CTOR", "L", "I2", "I4"),
        )
    }
    
    stats = builder.build(bindings, adjacency)
    
    assert stats.binding_count == 4
    assert stats.singleton_bindings == 2
    assert stats.transient_bindings == 1
    assert stats.scoped_bindings == 1
    assert stats.interface_count == 4
    assert stats.implementation_count == 4
    
    g_stats = stats.graph_statistics
    assert g_stats.edge_count == 3
    assert stats.required_dependency_count == 2
    assert stats.optional_dependency_count == 1
    
    assert g_stats.root_count == 1
    assert g_stats.leaf_count == 2
    assert g_stats.graph_depth == 3
    assert g_stats.graph_width > 0
    assert g_stats.connected_components == 1
    
def test_disconnected_components_statistics():
    builder = InjectionStatisticsBuilder()
    bindings = (
        RuntimeInjectionBinding("I1", "Impl1", "s1", "S", "G"),
        RuntimeInjectionBinding("I2", "Impl2", "s2", "S", "G"),
        RuntimeInjectionBinding("I3", "Impl3", "s3", "S", "G"),
    )
    adjacency = {
        "I1": (InjectionDescriptor("R", False, "C", "G", "I1", "I2"),)
        # I3 is disconnected
    }
    
    stats = builder.build(bindings, adjacency)
    g_stats = stats.graph_statistics
    
    assert g_stats.connected_components == 2
    assert g_stats.root_count == 2 # I1, I3
    assert g_stats.leaf_count == 2 # I2, I3
