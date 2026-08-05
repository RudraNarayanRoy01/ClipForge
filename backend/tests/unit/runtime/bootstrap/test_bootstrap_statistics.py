import pytest
from types import MappingProxyType
from src.runtime.bootstrap.bootstrap_statistics_builder import BootstrapStatisticsBuilder
from src.runtime.bootstrap.runtime_bootstrap_graph import RuntimeBootstrapGraph
from src.runtime.bootstrap.runtime_bootstrap_plan import RuntimeBootstrapPlan
from src.runtime.bootstrap.runtime_bootstrap_layer import RuntimeBootstrapLayer
from src.runtime.bootstrap.runtime_bootstrap_dependency_batch import RuntimeBootstrapDependencyBatch
from src.runtime.bootstrap.runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor


def test_statistics_builder():
    builder = BootstrapStatisticsBuilder()
    
    desc_a = RuntimeBootstrapDescriptor("a", "1.0", ("b",))
    desc_b = RuntimeBootstrapDescriptor("b", "1.0", ())
    
    graph = RuntimeBootstrapGraph(
        roots=frozenset(["a"]),
        leaves=frozenset(["b"]),
        descriptor_lookup=MappingProxyType({"a": desc_a, "b": desc_b}),
        dependency_lookup=MappingProxyType({"a": ("b",), "b": ()}),
        layer_lookup=MappingProxyType({}),
        adjacency_lookup=MappingProxyType({"a": ("b",), "b": ()}),
        reverse_adjacency_lookup=MappingProxyType({"b": ("a",), "a": ()})
    )
    
    batch = RuntimeBootstrapDependencyBatch("b1", (desc_a, desc_b), MappingProxyType({}))
    layer = RuntimeBootstrapLayer("l1", (batch,), MappingProxyType({}))
    plan = RuntimeBootstrapPlan((layer,))
    
    graph_stats, plan_stats = builder.build_statistics(graph, plan)
    
    assert graph_stats.node_count == 2
    assert graph_stats.edge_count == 1
    assert graph_stats.root_count == 1
    assert graph_stats.leaf_count == 1
    assert graph_stats.graph_depth == 2
    assert graph_stats.graph_width == 1 # a and b are at different levels
    assert graph_stats.connected_components == 1
    assert plan_stats.layer_count == 1
    assert plan_stats.dependency_batch_count == 1
    assert plan_stats.descriptor_count == 2
    assert plan_stats.planned_initialization_steps == 2
    assert plan_stats.bootstrap_group_count == 1
    assert plan_stats.planning_depth == 1
