import pytest
from types import MappingProxyType
from backend.src.runtime.injection.runtime_injection_composition import RuntimeInjectionComposition
from backend.src.runtime.injection.runtime_injection_binding import RuntimeInjectionBinding
from backend.src.runtime.injection.runtime_injection_graph import RuntimeInjectionGraph
from backend.src.runtime.injection.injection_metadata import InjectionMetadata
from backend.src.runtime.injection.injection_statistics import InjectionStatistics
from backend.src.runtime.injection.runtime_injection_graph_statistics import RuntimeInjectionGraphStatistics
from backend.src.runtime.injection.injection_snapshot import InjectionSnapshot


def _create_mock_objects():
    binding = RuntimeInjectionBinding("I", "Impl", "s1", "SINGLETON", "GLOBAL")
    graph = RuntimeInjectionGraph((binding,))
    metadata = InjectionMetadata("1.0", "1.0", 123.0)
    g_stats = RuntimeInjectionGraphStatistics(0, 1, 1, 1, 1, 0, 0, 0.0, 0, 0)
    stats = InjectionStatistics(1, 1, 1, 1, 0, 0, 0, 0, g_stats)
    snapshot = InjectionSnapshot("c1", graph, metadata, stats, "b_hash", "g_hash", "m_hash")
    return graph, metadata, stats, snapshot

def test_composition_immutability():
    graph, metadata, stats, snapshot = _create_mock_objects()

    composition = RuntimeInjectionComposition(
        composition_id="c1",
        graph=graph,
        metadata=metadata,
        statistics=stats,
        snapshot=snapshot
    )
    with pytest.raises(Exception):
        composition.composition_id = "c2"

def test_composition_initialization():
    graph, metadata, stats, snapshot = _create_mock_objects()

    composition = RuntimeInjectionComposition(
        composition_id="c1",
        graph=graph,
        metadata=metadata,
        statistics=stats,
        snapshot=snapshot
    )
    assert composition.composition_id == "c1"
    assert composition.graph == graph
    assert composition.metadata == metadata
    assert composition.statistics == stats
    assert composition.snapshot == snapshot

def test_composition_read_only_properties():
    graph, metadata, stats, snapshot = _create_mock_objects()
    composition = RuntimeInjectionComposition("c1", graph, metadata, stats, snapshot)
    
    with pytest.raises(AttributeError):
        del composition.graph
        
def test_composition_internal_fields_hidden():
    graph, metadata, stats, snapshot = _create_mock_objects()
    composition = RuntimeInjectionComposition("c1", graph, metadata, stats, snapshot)
    
    # Internal fields start with underscore
    assert hasattr(composition, "_composition_id")
    assert composition._composition_id == "c1"
    
def test_composition_hash_equality_not_implemented():
    # As it's a frozen dataclass without custom eq, eq works by field value
    graph, metadata, stats, snapshot = _create_mock_objects()
    c1 = RuntimeInjectionComposition("c1", graph, metadata, stats, snapshot)
    c2 = RuntimeInjectionComposition("c1", graph, metadata, stats, snapshot)
    assert c1 == c2
