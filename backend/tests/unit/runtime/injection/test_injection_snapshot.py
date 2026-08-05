import pytest
from types import MappingProxyType
from backend.src.runtime.injection.injection_snapshot import InjectionSnapshot
from backend.src.runtime.injection.injection_snapshot_factory import InjectionSnapshotFactory
from backend.src.runtime.injection.injection_metadata import InjectionMetadata
from backend.src.runtime.injection.injection_statistics import InjectionStatistics
from backend.src.runtime.injection.runtime_injection_graph_statistics import RuntimeInjectionGraphStatistics
from backend.src.runtime.injection.runtime_injection_binding import RuntimeInjectionBinding
from backend.src.runtime.injection.runtime_injection_graph import RuntimeInjectionGraph
from backend.src.runtime.injection.injection_graph_factory import InjectionGraphFactory


def _create_mock_data():
    binding = RuntimeInjectionBinding("I", "Impl", "s1", "SINGLETON", "GLOBAL")
    graph = InjectionGraphFactory().create((binding,), {})
    metadata = InjectionMetadata("1.0", "1.0", 123.0)
    g_stats = RuntimeInjectionGraphStatistics(0, 1, 1, 1, 1, 0, 0, 0.0, 0, 0)
    stats = InjectionStatistics(1, 1, 0, 0, 1, 1, 0, 0, g_stats)
    return graph, metadata, stats

def test_snapshot_immutability():
    graph, metadata, stats = _create_mock_data()
    snapshot = InjectionSnapshot("c1", graph, metadata, stats, "b_hash", "g_hash", "m_hash")
    with pytest.raises(Exception):
        snapshot.composition_id = "c2"

def test_snapshot_initialization():
    graph, metadata, stats = _create_mock_data()
    snapshot = InjectionSnapshot("c1", graph, metadata, stats, "b_hash", "g_hash", "m_hash")
    assert snapshot.composition_id == "c1"
    assert snapshot.graph == graph
    assert snapshot.metadata == metadata
    assert snapshot.statistics == stats
    assert snapshot.binding_hash == "b_hash"
    assert snapshot.graph_hash == "g_hash"
    assert snapshot.metadata_hash == "m_hash"

def test_snapshot_factory_generates_deterministic_hashes():
    factory = InjectionSnapshotFactory()
    graph, metadata, stats = _create_mock_data()
    
    snapshot1 = factory.create("c1", graph, metadata, stats)
    snapshot2 = factory.create("c2", graph, metadata, stats)
    
    assert snapshot1.binding_hash == snapshot2.binding_hash
    assert snapshot1.graph_hash == snapshot2.graph_hash
    assert snapshot1.metadata_hash == snapshot2.metadata_hash
    assert isinstance(snapshot1.binding_hash, str)
    assert len(snapshot1.binding_hash) == 64  # sha256
