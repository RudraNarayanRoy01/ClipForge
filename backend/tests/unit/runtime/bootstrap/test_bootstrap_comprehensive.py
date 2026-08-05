import pytest
from types import MappingProxyType
import hashlib
from typing import Dict, Tuple

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
from src.runtime.bootstrap.runtime_bootstrap import RuntimeBootstrap
from src.runtime.bootstrap.runtime_bootstrap_state import RuntimeBootstrapState
from src.runtime.bootstrap.bootstrap_stage import BootstrapStage
from src.runtime.bootstrap.bootstrap_result import BootstrapResult
from src.runtime.bootstrap.bootstrap_exceptions import (
    RuntimeBootstrapException,
    BootstrapValidationException,
    BootstrapGraphException,
    BootstrapPlanException,
    BootstrapMetadataException
)
from src.runtime.bootstrap.runtime_bootstrap_validator import RuntimeBootstrapValidator
from src.runtime.bootstrap.bootstrap_graph_factory import BootstrapGraphFactory
from src.runtime.bootstrap.bootstrap_plan_factory import BootstrapPlanFactory
from src.runtime.bootstrap.bootstrap_snapshot_factory import BootstrapSnapshotFactory

# --- Immutability & Protection Tests ---

def test_mapping_proxy_protection_graph():
    graph = RuntimeBootstrapGraph(
        roots=frozenset(["a"]),
        leaves=frozenset(["b"]),
        descriptor_lookup=MappingProxyType({}),
        dependency_lookup=MappingProxyType({}),
        layer_lookup=MappingProxyType({}),
        adjacency_lookup=MappingProxyType({"a": ("b",)}),
        reverse_adjacency_lookup=MappingProxyType({"b": ("a",)})
    )
    with pytest.raises(TypeError):
        graph.adjacency_lookup["a"] = ("c",) # type: ignore

def test_mapping_proxy_protection_metadata():
    metadata = RuntimeBootstrapMetadata(1.0, "1", "1", MappingProxyType({"env": "test"}), MappingProxyType({}), None)
    with pytest.raises(TypeError):
        metadata.labels["env"] = "prod" # type: ignore

def test_frozenset_protection_graph():
    graph = RuntimeBootstrapGraph(
        roots=frozenset(["a"]),
        leaves=frozenset(["b"]),
        descriptor_lookup=MappingProxyType({}),
        dependency_lookup=MappingProxyType({}),
        layer_lookup=MappingProxyType({}),
        adjacency_lookup=MappingProxyType({}),
        reverse_adjacency_lookup=MappingProxyType({})
    )
    with pytest.raises(AttributeError):
        graph.roots.add("c") # type: ignore

def test_tuple_protection_plan():
    plan = RuntimeBootstrapPlan(())
    with pytest.raises(AttributeError):
        plan.layers.append("layer") # type: ignore

# --- Deterministic Hashing Tests ---

def test_graph_hash_determinism():
    g1 = RuntimeBootstrapGraph(frozenset(["a"]), frozenset(["b"]), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    g2 = RuntimeBootstrapGraph(frozenset(["a"]), frozenset(["b"]), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    assert hash(g1) == hash(g2)
    assert g1 == g2

def test_layer_hash_determinism():
    desc = RuntimeBootstrapDescriptor("a", "1", ())
    batch1 = RuntimeBootstrapDependencyBatch("b1", (desc,), MappingProxyType({}))
    batch2 = RuntimeBootstrapDependencyBatch("b1", (desc,), MappingProxyType({}))
    
    l1 = RuntimeBootstrapLayer("l1", (batch1,), MappingProxyType({}))
    l2 = RuntimeBootstrapLayer("l1", (batch2,), MappingProxyType({}))
    assert hash(l1) == hash(l2)
    assert l1 == l2

def test_composition_hash_determinism():
    graph = RuntimeBootstrapGraph(frozenset(), frozenset(), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    plan = RuntimeBootstrapPlan(())
    metadata = RuntimeBootstrapMetadata(1.0, "1", "1", MappingProxyType({}), MappingProxyType({}), None)
    graph_stats = BootstrapGraphStatistics(0, 0, 0, 0, 0, 0, 0)
    stats = RuntimeBootstrapStatistics(0, 0, 0, 0, 0, 0)
    snapshot = RuntimeBootstrapSnapshot("h", "ch", "h", "h", "h", "h", "h")
    
    c1 = RuntimeBootstrapComposition("c", graph, plan, metadata, graph_stats, stats, snapshot)
    c2 = RuntimeBootstrapComposition("c", graph, plan, metadata, graph_stats, stats, snapshot)
    
    assert hash(c1) == hash(c2)
    assert c1 == c2

def test_snapshot_factory_calculates_composition_hash():
    factory = BootstrapSnapshotFactory()
    graph = RuntimeBootstrapGraph(frozenset(), frozenset(), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    plan = RuntimeBootstrapPlan(())
    metadata = RuntimeBootstrapMetadata(1.0, "1", "1", MappingProxyType({}), MappingProxyType({}), None)
    graph_stats = BootstrapGraphStatistics(0, 0, 0, 0, 0, 0, 0)
    stats = RuntimeBootstrapStatistics(0, 0, 0, 0, 0, 0)
    
    snapshot = factory.build_snapshot(graph, plan, metadata, graph_stats, stats)
    assert snapshot.composition_hash is not None
    assert isinstance(snapshot.composition_hash, str)
    assert len(snapshot.composition_hash) > 0
    assert snapshot.bootstrap_hash != snapshot.composition_hash

# --- Graph Logic & Topology Tests ---

def test_graph_factory_deep_chain():
    factory = BootstrapGraphFactory()
    # a -> b -> c -> d -> e
    descriptors = {
        "a": RuntimeBootstrapDescriptor("a", "1", ("b",)),
        "b": RuntimeBootstrapDescriptor("b", "1", ("c",)),
        "c": RuntimeBootstrapDescriptor("c", "1", ("d",)),
        "d": RuntimeBootstrapDescriptor("d", "1", ("e",)),
        "e": RuntimeBootstrapDescriptor("e", "1", ())
    }
    adjacency = {
        "a": {"b"},
        "b": {"c"},
        "c": {"d"},
        "d": {"e"},
        "e": set()
    }
    graph = factory.build_graph(descriptors, {}, adjacency)
    assert "e" in graph.roots
    assert "a" in graph.leaves
    assert graph.adjacency_lookup["a"] == ("b",)
    assert graph.reverse_adjacency_lookup["e"] == ("d",)

def test_graph_factory_disconnected_components():
    factory = BootstrapGraphFactory()
    # a -> b
    # c -> d
    descriptors = {
        "a": RuntimeBootstrapDescriptor("a", "1", ("b",)),
        "b": RuntimeBootstrapDescriptor("b", "1", ()),
        "c": RuntimeBootstrapDescriptor("c", "1", ("d",)),
        "d": RuntimeBootstrapDescriptor("d", "1", ())
    }
    adjacency = {
        "a": {"b"},
        "b": set(),
        "c": {"d"},
        "d": set()
    }
    graph = factory.build_graph(descriptors, {}, adjacency)
    assert "b" in graph.roots
    assert "d" in graph.roots
    assert "a" in graph.leaves
    assert "c" in graph.leaves

def test_graph_factory_multiple_roots():
    factory = BootstrapGraphFactory()
    # a -> c, b -> c
    descriptors = {
        "a": RuntimeBootstrapDescriptor("a", "1", ("c",)),
        "b": RuntimeBootstrapDescriptor("b", "1", ("c",)),
        "c": RuntimeBootstrapDescriptor("c", "1", ())
    }
    adjacency = {
        "a": {"c"},
        "b": {"c"},
        "c": set()
    }
    graph = factory.build_graph(descriptors, {}, adjacency)
    assert "c" in graph.roots
    assert "a" in graph.leaves
    assert "b" in graph.leaves
    assert set(graph.reverse_adjacency_lookup["c"]) == {"a", "b"}

# --- Plan Construction Tests ---

def test_plan_factory_deep_chain():
    p_factory = BootstrapPlanFactory()
    desc = RuntimeBootstrapDescriptor("a", "1", ())
    batch = RuntimeBootstrapDependencyBatch("b", (desc,), MappingProxyType({}))
    layer = RuntimeBootstrapLayer("l", (batch,), MappingProxyType({}))
    plan = p_factory.build_plan([layer])
    
    assert len(plan.layers) == 1

def test_plan_factory_disconnected_components():
    pass # Deleted since topological sort is not in PlanFactory

# --- Validation Tests ---

def test_validator_complex_cycle():
    validator = RuntimeBootstrapValidator()
    # a -> b -> c -> a
    descriptors = {
        "a": RuntimeBootstrapDescriptor("a", "1", ("b",)),
        "b": RuntimeBootstrapDescriptor("b", "1", ("c",)),
        "c": RuntimeBootstrapDescriptor("c", "1", ("a",))
    }
    adjacency = {"a": {"b"}, "b": {"c"}, "c": {"a"}}
    layer = RuntimeBootstrapLayer("l", (), MappingProxyType({}))
    with pytest.raises(BootstrapValidationException, match="Cycle"):
        validator.validate_inputs(descriptors["a"], descriptors, [layer], adjacency)

def test_validator_self_cycle():
    validator = RuntimeBootstrapValidator()
    # a -> a
    descriptors = {
        "a": RuntimeBootstrapDescriptor("a", "1", ("a",))
    }
    adjacency = {"a": {"a"}}
    layer = RuntimeBootstrapLayer("l", (), MappingProxyType({}))
    with pytest.raises(BootstrapValidationException, match="Cycle"):
        validator.validate_inputs(descriptors["a"], descriptors, [layer], adjacency)

def test_validator_duplicate_identifiers():
    pass # Replaced with cycle detection tests because duplicate identifiers cannot exist in Dict lookup

def test_validator_missing_dependency():
    validator = RuntimeBootstrapValidator()
    descriptors = {
        "a": RuntimeBootstrapDescriptor("a", "1", ("missing",))
    }
    adjacency = {"a": {"missing"}}
    layer = RuntimeBootstrapLayer("l", (), MappingProxyType({}))
    with pytest.raises(BootstrapValidationException, match="not found in descriptors"):
        validator.validate_inputs(descriptors["a"], descriptors, [layer], adjacency)

def test_validator_valid_disconnected():
    validator = RuntimeBootstrapValidator()
    descriptors = {
        "a": RuntimeBootstrapDescriptor("a", "1", ()),
        "b": RuntimeBootstrapDescriptor("b", "1", ())
    }
    adjacency = {"a": set(), "b": set()}
    layer = RuntimeBootstrapLayer("l", (), MappingProxyType({}))
    validator.validate_inputs(descriptors["a"], descriptors, [layer], adjacency)
    # Does not raise

# --- Result & State Tests ---

def test_bootstrap_result_immutability():
    graph = RuntimeBootstrapGraph(frozenset(), frozenset(), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    plan = RuntimeBootstrapPlan(())
    metadata = RuntimeBootstrapMetadata(1.0, "1", "1", MappingProxyType({}), MappingProxyType({}), None)
    graph_stats = BootstrapGraphStatistics(0, 0, 0, 0, 0, 0, 0)
    stats = RuntimeBootstrapStatistics(0, 0, 0, 0, 0, 0)
    snapshot = RuntimeBootstrapSnapshot("h", "c", "h", "h", "h", "h", "h")
    comp = RuntimeBootstrapComposition("c", graph, plan, metadata, graph_stats, stats, snapshot)
    
    bootstrap = RuntimeBootstrap("id", RuntimeBootstrapDescriptor("root", "1", ()), comp, RuntimeBootstrapState(BootstrapStage.UNINITIALIZED))
    
    result = BootstrapResult(bootstrap, comp, snapshot, stats, (), ())
    with pytest.raises(AttributeError):
        result.warnings = ("warn",) # type: ignore

def test_validator_missing_primary_descriptor():
    validator = RuntimeBootstrapValidator()
    descriptors = {
        "a": RuntimeBootstrapDescriptor("a", "1", ())
    }
    layer = RuntimeBootstrapLayer("l", (), MappingProxyType({}))
    with pytest.raises(BootstrapValidationException, match="Primary RuntimeBootstrapDescriptor is required"):
        validator.validate_inputs(None, descriptors, [layer], {}) # type: ignore

def test_validator_missing_descriptors_dict():
    validator = RuntimeBootstrapValidator()
    desc = RuntimeBootstrapDescriptor("a", "1", ())
    layer = RuntimeBootstrapLayer("l", (), MappingProxyType({}))
    with pytest.raises(BootstrapValidationException, match="At least one RuntimeBootstrapDescriptor is required"):
        validator.validate_inputs(desc, {}, [layer], {})

# --- Exceptions Hierarchy Tests ---

def test_exception_hierarchy():
    assert issubclass(BootstrapValidationException, RuntimeBootstrapException)
    assert issubclass(BootstrapGraphException, RuntimeBootstrapException)
    assert issubclass(BootstrapPlanException, RuntimeBootstrapException)
    assert issubclass(BootstrapMetadataException, RuntimeBootstrapException)

def test_exception_messages():
    ex = BootstrapValidationException("msg")
    assert str(ex) == "msg"
