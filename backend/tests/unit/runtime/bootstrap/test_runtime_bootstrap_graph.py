import pytest
from types import MappingProxyType
from src.runtime.bootstrap.runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor
from src.runtime.bootstrap.runtime_bootstrap_layer import RuntimeBootstrapLayer
from src.runtime.bootstrap.runtime_bootstrap_graph import RuntimeBootstrapGraph


def test_graph_immutability():
    graph = RuntimeBootstrapGraph(
        roots=frozenset(),
        leaves=frozenset(),
        descriptor_lookup=MappingProxyType({}),
        dependency_lookup=MappingProxyType({}),
        layer_lookup=MappingProxyType({}),
        adjacency_lookup=MappingProxyType({}),
        reverse_adjacency_lookup=MappingProxyType({})
    )
    
    with pytest.raises(AttributeError):
        graph.roots = frozenset(["a"]) # type: ignore
        
    with pytest.raises(AttributeError):
        graph.descriptor_lookup = MappingProxyType({}) # type: ignore

def test_lookup_mapping_proxy_enforcement():
    desc = RuntimeBootstrapDescriptor("test", "1.0", ())
    # This should fail or not be allowed, but __init__ converts dict to MappingProxyType
    graph = RuntimeBootstrapGraph(
        roots=frozenset(),
        leaves=frozenset(),
        descriptor_lookup=MappingProxyType({"test": desc}),
        dependency_lookup=MappingProxyType({}),
        layer_lookup=MappingProxyType({}),
        adjacency_lookup=MappingProxyType({}),
        reverse_adjacency_lookup=MappingProxyType({})
    )
    
    assert isinstance(graph.descriptor_lookup, MappingProxyType)
    
    with pytest.raises(TypeError):
        graph.descriptor_lookup["test2"] = desc # type: ignore

def test_graph_equality():
    graph1 = RuntimeBootstrapGraph(
        roots=frozenset(["a"]),
        leaves=frozenset(["b"]),
        descriptor_lookup=MappingProxyType({}),
        dependency_lookup=MappingProxyType({}),
        layer_lookup=MappingProxyType({}),
        adjacency_lookup=MappingProxyType({"a": ("b",)}),
        reverse_adjacency_lookup=MappingProxyType({"b": ("a",)})
    )
    graph2 = RuntimeBootstrapGraph(
        roots=frozenset(["a"]),
        leaves=frozenset(["b"]),
        descriptor_lookup=MappingProxyType({}),
        dependency_lookup=MappingProxyType({}),
        layer_lookup=MappingProxyType({}),
        adjacency_lookup=MappingProxyType({"a": ("b",)}),
        reverse_adjacency_lookup=MappingProxyType({"b": ("a",)})
    )
    
    assert graph1 == graph2
    assert hash(graph1) == hash(graph2)
