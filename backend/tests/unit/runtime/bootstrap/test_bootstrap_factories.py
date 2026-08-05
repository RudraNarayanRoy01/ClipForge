import pytest
from types import MappingProxyType
from src.runtime.bootstrap.bootstrap_id_factory import BootstrapIdFactory
from src.runtime.bootstrap.bootstrap_metadata_factory import BootstrapMetadataFactory
from src.runtime.bootstrap.bootstrap_graph_factory import BootstrapGraphFactory
from src.runtime.bootstrap.bootstrap_plan_factory import BootstrapPlanFactory
from src.runtime.bootstrap.runtime_bootstrap_factory import RuntimeBootstrapFactory
from src.runtime.bootstrap.runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor
from src.runtime.bootstrap.runtime_bootstrap_dependency_batch import RuntimeBootstrapDependencyBatch
from src.runtime.bootstrap.runtime_bootstrap_layer import RuntimeBootstrapLayer
from src.runtime.bootstrap.runtime_bootstrap_graph import RuntimeBootstrapGraph
from src.runtime.bootstrap.runtime_bootstrap_plan import RuntimeBootstrapPlan
from src.runtime.bootstrap.runtime_bootstrap_metadata import RuntimeBootstrapMetadata
from src.runtime.bootstrap.bootstrap_graph_statistics import BootstrapGraphStatistics
from src.runtime.bootstrap.runtime_bootstrap_statistics import RuntimeBootstrapStatistics
from src.runtime.bootstrap.runtime_bootstrap_snapshot import RuntimeBootstrapSnapshot
from src.runtime.bootstrap.runtime_bootstrap_composition import RuntimeBootstrapComposition


def test_id_factory_generates_unique_ids():
    factory = BootstrapIdFactory()
    id1 = factory.generate_composition_id()
    id2 = factory.generate_composition_id()
    assert id1 != id2
    assert id1.startswith("bootstrap_comp_")
    
    id3 = factory.generate_runtime_bootstrap_id()
    id4 = factory.generate_runtime_bootstrap_id()
    assert id3 != id4
    assert id3.startswith("runtime_bootstrap_")

def test_metadata_factory_creates_metadata():
    factory = BootstrapMetadataFactory()
    metadata = factory.create_metadata(
        version="1.0.0",
        schema_version="1.1",
        labels={"env": "prod"},
        annotations={"author": "test"},
        description="test desc"
    )
    
    assert metadata.version == "1.0.0"
    assert metadata.schema_version == "1.1"
    assert metadata.labels["env"] == "prod"
    assert metadata.annotations["author"] == "test"
    assert metadata.description == "test desc"
    assert metadata.created_at_utc > 0

def test_graph_factory_calculates_roots_and_leaves():
    factory = BootstrapGraphFactory()
    
    desc_a = RuntimeBootstrapDescriptor("a", "1.0", ("b",))
    desc_b = RuntimeBootstrapDescriptor("b", "1.0", ())
    
    descriptors = {"a": desc_a, "b": desc_b}
    adjacency = {"a": {"b"}, "b": set()}
    
    graph = factory.build_graph(descriptors, {}, adjacency)
    
    assert "b" in graph.roots
    assert "a" not in graph.roots
    assert "a" in graph.leaves
    assert "b" not in graph.leaves
    
    assert graph.adjacency_lookup["a"] == ("b",)
    assert graph.reverse_adjacency_lookup["b"] == ("a",)

def test_plan_factory_creates_plan():
    factory = BootstrapPlanFactory()
    layer = RuntimeBootstrapLayer("l1", (), MappingProxyType({}))
    plan = factory.build_plan([layer])
    
    assert len(plan.layers) == 1
    assert plan.layers[0] == layer

def test_runtime_bootstrap_factory():
    factory = RuntimeBootstrapFactory()
    
    desc = RuntimeBootstrapDescriptor("test", "1.0", ())
    graph = RuntimeBootstrapGraph(
        roots=frozenset(), leaves=frozenset(), descriptor_lookup=MappingProxyType({}),
        dependency_lookup=MappingProxyType({}), layer_lookup=MappingProxyType({}),
        adjacency_lookup=MappingProxyType({}), reverse_adjacency_lookup=MappingProxyType({})
    )
    plan = RuntimeBootstrapPlan(())
    metadata = RuntimeBootstrapMetadata(1.0, "1", "1", MappingProxyType({}), MappingProxyType({}), None)
    graph_stats = BootstrapGraphStatistics(0, 0, 0, 0, 0, 0, 0)
    stats = RuntimeBootstrapStatistics(0, 0, 0, 0, 0, 0)
    snapshot = RuntimeBootstrapSnapshot("h", "h", "h", "h", "h", "h", "h")
    
    comp = RuntimeBootstrapComposition("comp", graph, plan, metadata, graph_stats, stats, snapshot)
    
    bootstrap = factory.build_bootstrap("boot_1", desc, comp)
    
    assert bootstrap.identifier == "boot_1"
    assert bootstrap.descriptor == desc
    assert bootstrap.composition == comp
    assert bootstrap.state.stage.value == "READY"
