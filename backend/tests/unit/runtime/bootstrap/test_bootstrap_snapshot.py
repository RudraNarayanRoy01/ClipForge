import pytest
from types import MappingProxyType
from src.runtime.bootstrap.bootstrap_snapshot_factory import BootstrapSnapshotFactory
from src.runtime.bootstrap.runtime_bootstrap_graph import RuntimeBootstrapGraph
from src.runtime.bootstrap.runtime_bootstrap_plan import RuntimeBootstrapPlan
from src.runtime.bootstrap.runtime_bootstrap_metadata import RuntimeBootstrapMetadata
from src.runtime.bootstrap.bootstrap_graph_statistics import BootstrapGraphStatistics
from src.runtime.bootstrap.runtime_bootstrap_statistics import RuntimeBootstrapStatistics


def test_snapshot_hash_determinism():
    factory = BootstrapSnapshotFactory()
    
    graph = RuntimeBootstrapGraph(
        roots=frozenset(["a"]),
        leaves=frozenset(["b"]),
        descriptor_lookup=MappingProxyType({}),
        dependency_lookup=MappingProxyType({}),
        layer_lookup=MappingProxyType({}),
        adjacency_lookup=MappingProxyType({"a": ("b",)}),
        reverse_adjacency_lookup=MappingProxyType({"b": ("a",)})
    )
    plan = RuntimeBootstrapPlan(())
    metadata = RuntimeBootstrapMetadata(1.0, "1", "1", MappingProxyType({}), MappingProxyType({}), None)
    graph_stats = BootstrapGraphStatistics(2, 1, 1, 1, 2, 1, 1)
    stats = RuntimeBootstrapStatistics(0, 0, 0, 0, 0, 0)
    
    snapshot1 = factory.build_snapshot(graph, plan, metadata, graph_stats, stats)
    snapshot2 = factory.build_snapshot(graph, plan, metadata, graph_stats, stats)
    
    assert snapshot1.bootstrap_hash == snapshot2.bootstrap_hash
    assert snapshot1.composition_hash == snapshot2.composition_hash
    assert snapshot1.graph_hash == snapshot2.graph_hash
    assert snapshot1.plan_hash == snapshot2.plan_hash
    assert snapshot1.metadata_hash == snapshot2.metadata_hash
    assert snapshot1.graph_statistics_hash == snapshot2.graph_statistics_hash
    assert snapshot1.statistics_hash == snapshot2.statistics_hash
