import pytest
from backend.src.runtime.injection.runtime_injection_graph import RuntimeInjectionGraph
from backend.src.runtime.injection.runtime_injection_binding import RuntimeInjectionBinding
from backend.src.runtime.injection.injection_graph_factory import InjectionGraphFactory
from backend.src.runtime.injection.injection_descriptor import InjectionDescriptor
from types import MappingProxyType

def test_graph_immutability():
    binding = RuntimeInjectionBinding("I", "Impl", "s1", "SINGLETON", "GLOBAL")
    graph = RuntimeInjectionGraph((binding,))
    
    with pytest.raises(Exception):
        graph.bindings = ()

def test_graph_factory_lookups():
    factory = InjectionGraphFactory()
    binding1 = RuntimeInjectionBinding("I1", "Impl1", "s1", "SINGLETON", "GLOBAL")
    binding2 = RuntimeInjectionBinding("I2", "Impl2", "s2", "SINGLETON", "GLOBAL")
    
    graph = factory.create((binding1, binding2), {})
    
    assert "I1" in graph.interface_lookup
    assert graph.binding_lookup["s1"] == binding1
    assert len(graph.implementation_lookup["Impl2"]) == 1

def test_graph_factory_roots_and_leaves():
    factory = InjectionGraphFactory()
    binding1 = RuntimeInjectionBinding("I1", "Impl1", "s1", "S", "G")
    binding2 = RuntimeInjectionBinding("I2", "Impl2", "s2", "S", "G")
    binding3 = RuntimeInjectionBinding("I3", "Impl3", "s3", "S", "G")
    
    adj = {
        "I1": (InjectionDescriptor("R", False, "C", "G", "I1", "I2"),),
        "I2": (InjectionDescriptor("R", False, "C", "G", "I2", "I3"),)
    }
    
    graph = factory.create((binding1, binding2, binding3), adj)
    
    assert "I1" in graph.roots
    assert "I3" not in graph.roots
    assert "I3" in graph.leaves
    assert "I1" not in graph.leaves

def test_graph_factory_reverse_adjacency():
    factory = InjectionGraphFactory()
    binding1 = RuntimeInjectionBinding("I1", "Impl1", "s1", "S", "G")
    binding2 = RuntimeInjectionBinding("I2", "Impl2", "s2", "S", "G")
    
    adj = {
        "I1": (InjectionDescriptor("R", False, "C", "G", "I1", "I2"),)
    }
    
    graph = factory.create((binding1, binding2), adj)
    
    assert "I2" in graph.reverse_adjacency
    assert graph.reverse_adjacency["I2"] == ("I1",)

def test_graph_factory_disconnected_components():
    factory = InjectionGraphFactory()
    binding1 = RuntimeInjectionBinding("I1", "Impl1", "s1", "S", "G")
    binding2 = RuntimeInjectionBinding("I2", "Impl2", "s2", "S", "G")
    
    graph = factory.create((binding1, binding2), {})
    
    assert len(graph.roots) == 2
    assert len(graph.leaves) == 2

def test_graph_lookups_are_mapping_proxies():
    factory = InjectionGraphFactory()
    binding = RuntimeInjectionBinding("I", "Impl", "s", "S", "G")
    graph = factory.create((binding,), {})
    
    assert isinstance(graph.binding_lookup, MappingProxyType)
    assert isinstance(graph.interface_lookup, MappingProxyType)
    assert isinstance(graph.implementation_lookup, MappingProxyType)
