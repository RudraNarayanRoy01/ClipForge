import pytest
from backend.src.runtime.injection.injection_id_factory import InjectionIdFactory
from backend.src.runtime.injection.injection_metadata_factory import InjectionMetadataFactory
from backend.src.runtime.injection.runtime_injection_factory import RuntimeInjectionFactory
from backend.src.runtime.injection.injection_graph_factory import InjectionGraphFactory
from backend.src.runtime.injection.injection_snapshot import InjectionSnapshot
from backend.src.runtime.injection.injection_statistics import InjectionStatistics
from backend.src.runtime.injection.runtime_injection_graph_statistics import RuntimeInjectionGraphStatistics
from backend.src.runtime.injection.runtime_injection_binding import RuntimeInjectionBinding


def test_id_factory_generates_unique_composition_ids():
    factory = InjectionIdFactory()
    id1 = factory.create()
    id2 = factory.create()
    assert id1 != id2
    assert id1.startswith("composition-")

def test_metadata_factory_defaults():
    factory = InjectionMetadataFactory()
    metadata = factory.create()
    assert metadata.schema_version == "1.0"
    assert metadata.builder_version == "1.0.0"
    assert metadata.creation_timestamp > 0

def test_metadata_factory_custom_builder_version():
    factory = InjectionMetadataFactory()
    metadata = factory.create("2.0.0")
    assert metadata.builder_version == "2.0.0"

def test_runtime_injection_factory():
    factory = RuntimeInjectionFactory()
    
    bindings = (RuntimeInjectionBinding("I", "Impl", "s", "SINGLETON", "GLOBAL"),)
    graph = InjectionGraphFactory().create(bindings, {})
    metadata = InjectionMetadataFactory().create()
    g_stats = RuntimeInjectionGraphStatistics(0,1,1,1,1,0,0,0.0,0,0)
    stats = InjectionStatistics(1,1,1,1,0,0,0,0,g_stats)
    snapshot = InjectionSnapshot("c1", graph, metadata, stats, "b", "g", "m")
    
    composition = factory.create(
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

def test_factories_do_not_share_state():
    # Each factory should be pure
    id_factory1 = InjectionIdFactory()
    id_factory2 = InjectionIdFactory()
    assert id_factory1 is not id_factory2
