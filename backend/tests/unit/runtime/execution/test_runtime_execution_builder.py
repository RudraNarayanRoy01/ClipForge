import pytest
import dataclasses
import hashlib
import json
from types import MappingProxyType

from src.runtime.execution.runtime_execution_builder_descriptor import RuntimeExecutionBuilderDescriptor
from src.runtime.execution.runtime_execution_builder_metadata import RuntimeExecutionBuilderMetadata
from src.runtime.execution.runtime_execution_builder_statistics import RuntimeExecutionBuilderStatistics
from src.runtime.execution.runtime_execution_builder_snapshot import RuntimeExecutionBuilderSnapshot
from src.runtime.execution.runtime_execution_builder_identity import RuntimeExecutionBuilderIdentity
from src.runtime.execution.runtime_execution_builder import RuntimeExecutionBuilder
from src.runtime.execution.runtime_execution_builder_validator import RuntimeExecutionBuilderValidator

from src.runtime.execution.execution_builder_descriptor_factory import ExecutionBuilderDescriptorFactory
from src.runtime.execution.execution_builder_metadata_factory import ExecutionBuilderMetadataFactory
from src.runtime.execution.execution_builder_statistics_builder import ExecutionBuilderStatisticsBuilder
from src.runtime.execution.execution_builder_snapshot_factory import ExecutionBuilderSnapshotFactory
from src.runtime.execution.execution_builder_factory import ExecutionBuilderFactory
from src.runtime.execution.runtime_execution_builder_factory import RuntimeExecutionBuilderFactory

from src.runtime.execution.runtime_execution_composition import RuntimeExecutionComposition

class MockSnapshot:
    composition_hash = "mock_comp_hash"

class MockIdentity:
    snapshot = MockSnapshot()

class MockComposition:
    identifier = "comp-123"
    identity = MockIdentity()

@pytest.fixture
def mock_composition():
    return MockComposition()

@pytest.fixture
def base_args(mock_composition):
    return {
        "execution_id": "exec-123",
        "runtime_id": "rt-123",
        "graph_id": "graph-123",
        "plan_id": "plan-123",
        "context_id": "ctx-123",
        "composition_id": "comp-123",
        "builder_id": "bld-123",
        "composition": mock_composition,
        "composition_lookup": {"comp-123": mock_composition},
        "descriptor_lookup": {"bld-123": "self_descriptor_mock"},
        "builder_lookup": {"bld-123": "self_mock"},
        "labels": {"env": "test"},
        "annotations": {"test": "true"},
        "tags": {"v1"}
    }

# --- Descriptor Tests (10 tests) ---
def test_descriptor_is_dataclass():
    desc = ExecutionBuilderDescriptorFactory.create("a", "b", "c", "d", "e", "f", "g", "1.0", "1.0")
    assert dataclasses.is_dataclass(desc)

def test_descriptor_is_frozen():
    desc = ExecutionBuilderDescriptorFactory.create("a", "b", "c", "d", "e", "f", "g", "1.0", "1.0")
    with pytest.raises(dataclasses.FrozenInstanceError):
        desc.execution_id = "new"

def test_descriptor_ownership():
    desc = ExecutionBuilderDescriptorFactory.create("a", "b", "c", "d", "e", "f", "g", "v", "s")
    assert desc.execution_id == "a"
    assert desc.runtime_id == "b"
    assert desc.graph_id == "c"
    assert desc.plan_id == "d"
    assert desc.context_id == "e"
    assert desc.composition_id == "f"
    assert desc.builder_id == "g"
    assert desc.version == "v"
    assert desc.schema_version == "s"

def test_descriptor_no_execute():
    desc = ExecutionBuilderDescriptorFactory.create("a", "b", "c", "d", "e", "f", "g", "v", "s")
    assert not hasattr(desc, "execute")

def test_descriptor_no_schedule():
    desc = ExecutionBuilderDescriptorFactory.create("a", "b", "c", "d", "e", "f", "g", "v", "s")
    assert not hasattr(desc, "schedule")

def test_descriptor_no_run():
    desc = ExecutionBuilderDescriptorFactory.create("a", "b", "c", "d", "e", "f", "g", "v", "s")
    assert not hasattr(desc, "run")

def test_descriptor_factory_returns_descriptor():
    desc = ExecutionBuilderDescriptorFactory.create("a", "b", "c", "d", "e", "f", "g", "v", "s")
    assert isinstance(desc, RuntimeExecutionBuilderDescriptor)

def test_descriptor_preserves_empty_strings():
    desc = ExecutionBuilderDescriptorFactory.create("", "", "", "", "", "", "", "", "")
    assert desc.execution_id == ""

def test_descriptor_all_fields_present():
    desc = ExecutionBuilderDescriptorFactory.create("a", "b", "c", "d", "e", "f", "g", "v", "s")
    fields = [f.name for f in dataclasses.fields(desc)]
    assert set(fields) == {"execution_id", "runtime_id", "graph_id", "plan_id", "context_id", "composition_id", "builder_id", "version", "schema_version"}

def test_descriptor_type_hints():
    assert RuntimeExecutionBuilderDescriptor.__annotations__["builder_id"] == str


# --- Metadata Tests (10 tests) ---
def test_metadata_is_frozen_dataclass():
    meta = ExecutionBuilderMetadataFactory.create({"a": "1"}, {"b": "2"}, {"t1"})
    assert dataclasses.is_dataclass(meta)
    with pytest.raises(dataclasses.FrozenInstanceError):
        meta.labels = MappingProxyType({})

def test_metadata_ownership():
    meta = ExecutionBuilderMetadataFactory.create({"a": "1"}, {"b": "2"}, {"t1"})
    assert "a" in meta.labels
    assert "b" in meta.annotations
    assert "t1" in meta.tags

def test_metadata_labels_is_mappingproxy():
    meta = ExecutionBuilderMetadataFactory.create({"a": "1"}, {}, set())
    assert isinstance(meta.labels, MappingProxyType)

def test_metadata_annotations_is_mappingproxy():
    meta = ExecutionBuilderMetadataFactory.create({}, {"b": "2"}, set())
    assert isinstance(meta.annotations, MappingProxyType)

def test_metadata_tags_is_frozenset():
    meta = ExecutionBuilderMetadataFactory.create({}, {}, {"t1"})
    assert isinstance(meta.tags, frozenset)

def test_metadata_labels_immutability():
    meta = ExecutionBuilderMetadataFactory.create({"a": "1"}, {}, set())
    with pytest.raises(TypeError):
        meta.labels["a"] = "2"

def test_metadata_factory_isolation_labels():
    orig_labels = {"a": "1"}
    meta = ExecutionBuilderMetadataFactory.create(orig_labels, {}, set())
    orig_labels["a"] = "2"
    assert meta.labels["a"] == "1"

def test_metadata_factory_isolation_annotations():
    orig_ann = {"a": "1"}
    meta = ExecutionBuilderMetadataFactory.create({}, orig_ann, set())
    orig_ann["a"] = "2"
    assert meta.annotations["a"] == "1"

def test_metadata_factory_isolation_tags():
    orig_tags = {"t1"}
    meta = ExecutionBuilderMetadataFactory.create({}, {}, orig_tags)
    orig_tags.add("t2")
    assert "t2" not in meta.tags

def test_metadata_no_execution_behavior():
    meta = ExecutionBuilderMetadataFactory.create({}, {}, set())
    assert not hasattr(meta, "execute")


# --- Statistics Tests (10 tests) ---
def test_statistics_is_frozen_dataclass():
    stat = ExecutionBuilderStatisticsBuilder.build(None, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    assert dataclasses.is_dataclass(stat)
    with pytest.raises(dataclasses.FrozenInstanceError):
        stat.composition_count = 1

def test_statistics_ownership():
    stat = ExecutionBuilderStatisticsBuilder.build(MockComposition(), MappingProxyType({"c": 1, "d": 2}), MappingProxyType({"e": 1}), MappingProxyType({"f": 1}))
    assert stat.composition_count == 1
    assert stat.composition_lookup_count == 2
    assert stat.descriptor_lookup_count == 1
    assert stat.builder_lookup_count == 1

def test_statistics_no_performance_metrics(mock_composition):
    stat = ExecutionBuilderStatisticsBuilder.build(mock_composition, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    fields = {f.name for f in dataclasses.fields(stat)}
    assert "latency" not in fields
    assert "cpu_usage" not in fields
    assert "memory" not in fields

def test_statistics_zero_counts():
    stat = ExecutionBuilderStatisticsBuilder.build(None, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    assert stat.composition_count == 0
    assert stat.composition_lookup_count == 0

def test_statistics_builder_no_state(mock_composition):
    builder = ExecutionBuilderStatisticsBuilder()
    assert not hasattr(builder, "state")

def test_statistics_no_execution_methods(mock_composition):
    stat = ExecutionBuilderStatisticsBuilder.build(mock_composition, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    assert not hasattr(stat, "run")
    assert not hasattr(stat, "start")

def test_statistics_type_hints(mock_composition):
    assert RuntimeExecutionBuilderStatistics.__annotations__["composition_count"] == int

def test_statistics_factory_returns_statistics(mock_composition):
    stat = ExecutionBuilderStatisticsBuilder.build(mock_composition, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    assert isinstance(stat, RuntimeExecutionBuilderStatistics)

def test_statistics_exact_fields():
    fields = {f.name for f in dataclasses.fields(RuntimeExecutionBuilderStatistics)}
    assert fields == {"composition_count", "composition_lookup_count", "descriptor_lookup_count", "builder_lookup_count"}

def test_statistics_determinism(mock_composition):
    stat1 = ExecutionBuilderStatisticsBuilder.build(mock_composition, MappingProxyType({"a":1}), MappingProxyType({}), MappingProxyType({}))
    stat2 = ExecutionBuilderStatisticsBuilder.build(mock_composition, MappingProxyType({"a":1}), MappingProxyType({}), MappingProxyType({}))
    assert stat1 == stat2


# --- Snapshot Tests (15 tests) ---
@pytest.fixture
def snapshot_deps(mock_composition):
    desc = ExecutionBuilderDescriptorFactory.create("a","b","c","d","e","f","g","v","s")
    meta = ExecutionBuilderMetadataFactory.create({"a": "1"}, {"b": "2"}, {"t1"})
    stat = ExecutionBuilderStatisticsBuilder.build(mock_composition, MappingProxyType({"f": mock_composition}), MappingProxyType({"g": desc}), MappingProxyType({"g": "self"}))
    return {
        "descriptor": desc,
        "composition": mock_composition,
        "composition_lookup": {"f": mock_composition},
        "descriptor_lookup": {"g": desc},
        "builder_lookup": {"g": "self"},
        "metadata": meta,
        "statistics": stat
    }

def test_snapshot_is_frozen_dataclass(snapshot_deps):
    snap = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
    assert dataclasses.is_dataclass(snap)
    with pytest.raises(dataclasses.FrozenInstanceError):
        snap.builder_hash = "new"

def test_snapshot_ownership(snapshot_deps):
    snap = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
    assert snap.descriptor_hash
    assert snap.composition_hash
    assert snap.composition_lookup_hash
    assert snap.descriptor_lookup_hash
    assert snap.builder_lookup_hash
    assert snap.metadata_hash
    assert snap.statistics_hash
    assert snap.builder_hash

def test_snapshot_determinism(snapshot_deps):
    snap1 = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
    snap2 = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
    assert snap1 == snap2
    assert snap1.builder_hash == snap2.builder_hash

def test_snapshot_insertion_order_independence(snapshot_deps):
    deps1 = dict(snapshot_deps)
    deps1["composition_lookup"] = {"f": MockComposition(), "z": MockComposition()}
    
    deps2 = dict(snapshot_deps)
    deps2["composition_lookup"] = {"z": MockComposition(), "f": MockComposition()}
    
    snap1 = ExecutionBuilderSnapshotFactory.create(**deps1)
    snap2 = ExecutionBuilderSnapshotFactory.create(**deps2)
    assert snap1.composition_lookup_hash == snap2.composition_lookup_hash
    assert snap1.builder_hash == snap2.builder_hash

def test_snapshot_metadata_insertion_order_independence(snapshot_deps):
    deps1 = dict(snapshot_deps)
    deps1["metadata"] = ExecutionBuilderMetadataFactory.create({"a": "1", "z": "2"}, {}, set())
    
    deps2 = dict(snapshot_deps)
    deps2["metadata"] = ExecutionBuilderMetadataFactory.create({"z": "2", "a": "1"}, {}, set())
    
    snap1 = ExecutionBuilderSnapshotFactory.create(**deps1)
    snap2 = ExecutionBuilderSnapshotFactory.create(**deps2)
    assert snap1.metadata_hash == snap2.metadata_hash
    assert snap1.builder_hash == snap2.builder_hash

def test_snapshot_tags_order_independence(snapshot_deps):
    deps1 = dict(snapshot_deps)
    deps1["metadata"] = ExecutionBuilderMetadataFactory.create({}, {}, {"t1", "t2"})
    
    deps2 = dict(snapshot_deps)
    deps2["metadata"] = ExecutionBuilderMetadataFactory.create({}, {}, {"t2", "t1"})
    
    snap1 = ExecutionBuilderSnapshotFactory.create(**deps1)
    snap2 = ExecutionBuilderSnapshotFactory.create(**deps2)
    assert snap1.metadata_hash == snap2.metadata_hash
    assert snap1.builder_hash == snap2.builder_hash

def test_snapshot_hash_changes_with_descriptor(snapshot_deps):
    snap1 = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
    deps2 = dict(snapshot_deps)
    deps2["descriptor"] = ExecutionBuilderDescriptorFactory.create("z","b","c","d","e","f","g","v","s")
    snap2 = ExecutionBuilderSnapshotFactory.create(**deps2)
    assert snap1.descriptor_hash != snap2.descriptor_hash
    assert snap1.builder_hash != snap2.builder_hash

def test_snapshot_hash_changes_with_statistics(snapshot_deps):
    snap1 = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
    deps2 = dict(snapshot_deps)
    deps2["statistics"] = ExecutionBuilderStatisticsBuilder.build(None, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    snap2 = ExecutionBuilderSnapshotFactory.create(**deps2)
    assert snap1.statistics_hash != snap2.statistics_hash
    assert snap1.builder_hash != snap2.builder_hash

def test_snapshot_exact_fields():
    fields = {f.name for f in dataclasses.fields(RuntimeExecutionBuilderSnapshot)}
    assert fields == {"descriptor_hash", "composition_hash", "composition_lookup_hash", "descriptor_lookup_hash", "builder_lookup_hash", "metadata_hash", "statistics_hash", "builder_hash"}

def test_snapshot_no_timestamps(snapshot_deps):
    snap1 = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
    import time
    time.sleep(0.01)
    snap2 = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
    assert snap1.builder_hash == snap2.builder_hash

def test_snapshot_no_randomness(snapshot_deps):
    hashes = set()
    for _ in range(10):
        snap = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
        hashes.add(snap.builder_hash)
    assert len(hashes) == 1

def test_snapshot_no_uuid_generation(snapshot_deps):
    snap = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
    # Check if hash looks like a sha256 hex string and not a UUID
    assert len(snap.builder_hash) == 64
    assert "-" not in snap.builder_hash

def test_snapshot_no_execution_behavior(snapshot_deps):
    snap = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
    assert not hasattr(snap, "execute")

def test_snapshot_all_hashes_are_sha256(snapshot_deps):
    snap = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
    for field in dataclasses.fields(snap):
        val = getattr(snap, field.name)
        assert isinstance(val, str)
        assert len(val) == 64
        int(val, 16) # Should be valid hex

def test_snapshot_factory_returns_snapshot(snapshot_deps):
    snap = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
    assert isinstance(snap, RuntimeExecutionBuilderSnapshot)


# --- Identity Tests (10 tests) ---
@pytest.fixture
def identity_deps(snapshot_deps):
    snap = ExecutionBuilderSnapshotFactory.create(**snapshot_deps)
    deps = dict(snapshot_deps)
    deps["snapshot"] = snap
    deps["composition_lookup"] = MappingProxyType(deps["composition_lookup"])
    deps["descriptor_lookup"] = MappingProxyType(deps["descriptor_lookup"])
    deps["builder_lookup"] = MappingProxyType(deps["builder_lookup"])
    return deps

def test_identity_is_frozen_dataclass(identity_deps):
    ident = ExecutionBuilderFactory.create(**identity_deps)
    assert dataclasses.is_dataclass(ident)
    with pytest.raises(dataclasses.FrozenInstanceError):
        ident.descriptor = None

def test_identity_ownership(identity_deps):
    ident = ExecutionBuilderFactory.create(**identity_deps)
    assert ident.descriptor == identity_deps["descriptor"]
    assert ident.metadata == identity_deps["metadata"]
    assert ident.statistics == identity_deps["statistics"]
    assert ident.snapshot == identity_deps["snapshot"]
    assert ident.composition == identity_deps["composition"]
    assert ident.composition_lookup == identity_deps["composition_lookup"]
    assert ident.descriptor_lookup == identity_deps["descriptor_lookup"]
    assert ident.builder_lookup == identity_deps["builder_lookup"]

def test_identity_lookups_are_mapping_proxies(identity_deps):
    ident = ExecutionBuilderFactory.create(**identity_deps)
    assert isinstance(ident.composition_lookup, MappingProxyType)
    assert isinstance(ident.descriptor_lookup, MappingProxyType)
    assert isinstance(ident.builder_lookup, MappingProxyType)

def test_identity_exact_fields():
    fields = {f.name for f in dataclasses.fields(RuntimeExecutionBuilderIdentity)}
    assert fields == {"descriptor", "metadata", "statistics", "snapshot", "composition", "composition_lookup", "descriptor_lookup", "builder_lookup"}

def test_identity_no_execution_behavior(identity_deps):
    ident = ExecutionBuilderFactory.create(**identity_deps)
    assert not hasattr(ident, "execute")

def test_identity_determinism(identity_deps):
    ident1 = ExecutionBuilderFactory.create(**identity_deps)
    ident2 = ExecutionBuilderFactory.create(**identity_deps)
    assert ident1 == ident2

def test_identity_factory_returns_identity(identity_deps):
    ident = ExecutionBuilderFactory.create(**identity_deps)
    assert isinstance(ident, RuntimeExecutionBuilderIdentity)

def test_identity_no_state_mutation(identity_deps):
    ident = ExecutionBuilderFactory.create(**identity_deps)
    with pytest.raises(TypeError):
        ident.composition_lookup["new"] = "val"

def test_identity_type_hints(identity_deps):
    assert RuntimeExecutionBuilderIdentity.__annotations__["composition_lookup"] == MappingProxyType[str, RuntimeExecutionComposition]

def test_identity_no_run_method(identity_deps):
    ident = ExecutionBuilderFactory.create(**identity_deps)
    assert not hasattr(ident, "run")


# --- Builder & Validator Tests (20 tests) ---
def test_builder_is_frozen_dataclass(identity_deps):
    ident = ExecutionBuilderFactory.create(**identity_deps)
    builder = RuntimeExecutionBuilderFactory.create("g", ident)
    assert dataclasses.is_dataclass(builder)
    with pytest.raises(dataclasses.FrozenInstanceError):
        builder.identifier = "new"

def test_builder_ownership(identity_deps):
    ident = ExecutionBuilderFactory.create(**identity_deps)
    builder = RuntimeExecutionBuilderFactory.create("g", ident)
    assert builder.identifier == "g"
    assert builder.identity == ident

def test_builder_exact_fields(identity_deps):
    fields = {f.name for f in dataclasses.fields(RuntimeExecutionBuilder)}
    assert fields == {"identifier", "identity"}

def test_builder_no_execution_behavior(identity_deps):
    ident = ExecutionBuilderFactory.create(**identity_deps)
    builder = RuntimeExecutionBuilderFactory.create("g", ident)
    assert not hasattr(builder, "execute")
    assert not hasattr(builder, "run")
    assert not hasattr(builder, "schedule")

def test_validator_detects_empty_identifier(identity_deps):
    ident = ExecutionBuilderFactory.create(**identity_deps)
    with pytest.raises(ValueError, match="Builder identifier cannot be empty"):
        RuntimeExecutionBuilderFactory.create("", ident)

def test_validator_detects_none_identity():
    with pytest.raises(ValueError, match="Builder identity cannot be None"):
        builder = RuntimeExecutionBuilder(identifier="g", identity=None)
        RuntimeExecutionBuilderValidator.validate(builder)

def test_validator_detects_missing_descriptor(identity_deps):
    deps = dict(identity_deps)
    deps["descriptor"] = None
    ident = RuntimeExecutionBuilderIdentity(**deps)
    builder = RuntimeExecutionBuilder("g", ident)
    with pytest.raises(ValueError, match="Builder descriptor cannot be None"):
        RuntimeExecutionBuilderValidator.validate(builder)

def test_validator_detects_missing_metadata(identity_deps):
    deps = dict(identity_deps)
    deps["metadata"] = None
    ident = RuntimeExecutionBuilderIdentity(**deps)
    builder = RuntimeExecutionBuilder("g", ident)
    with pytest.raises(ValueError, match="Builder metadata cannot be None"):
        RuntimeExecutionBuilderValidator.validate(builder)

def test_validator_detects_missing_statistics(identity_deps):
    deps = dict(identity_deps)
    deps["statistics"] = None
    ident = RuntimeExecutionBuilderIdentity(**deps)
    builder = RuntimeExecutionBuilder("g", ident)
    with pytest.raises(ValueError, match="Builder statistics cannot be None"):
        RuntimeExecutionBuilderValidator.validate(builder)

def test_validator_detects_missing_snapshot(identity_deps):
    deps = dict(identity_deps)
    deps["snapshot"] = None
    ident = RuntimeExecutionBuilderIdentity(**deps)
    builder = RuntimeExecutionBuilder("g", ident)
    with pytest.raises(ValueError, match="Builder snapshot cannot be None"):
        RuntimeExecutionBuilderValidator.validate(builder)

def test_validator_detects_missing_composition(identity_deps):
    deps = dict(identity_deps)
    deps["composition"] = None
    ident = RuntimeExecutionBuilderIdentity(**deps)
    builder = RuntimeExecutionBuilder("g", ident)
    with pytest.raises(ValueError, match="Execution composition cannot be None"):
        RuntimeExecutionBuilderValidator.validate(builder)

def test_validator_descriptor_id_mismatch(identity_deps):
    ident = ExecutionBuilderFactory.create(**identity_deps)
    with pytest.raises(ValueError, match="Descriptor builder_id must match builder identifier"):
        RuntimeExecutionBuilderFactory.create("different", ident)

def test_validator_duplicate_identifiers(identity_deps):
    deps = dict(identity_deps)
    # create duplicate id
    desc = ExecutionBuilderDescriptorFactory.create("a","a","c","d","e","f","g","v","s")
    deps["descriptor"] = desc
    ident = ExecutionBuilderFactory.create(**deps)
    with pytest.raises(ValueError, match="Duplicate identifiers detected across execution components"):
        RuntimeExecutionBuilderFactory.create("g", ident)

def test_validator_missing_builder_lookup(identity_deps):
    deps = dict(identity_deps)
    deps["builder_lookup"] = MappingProxyType({"other": "mock"})
    ident = ExecutionBuilderFactory.create(**deps)
    with pytest.raises(ValueError, match="Builder identifier must exist in builder_lookup"):
        RuntimeExecutionBuilderFactory.create("g", ident)

def test_validator_missing_composition_lookup(identity_deps):
    deps = dict(identity_deps)
    deps["composition_lookup"] = MappingProxyType({"other": identity_deps["composition"]})
    ident = ExecutionBuilderFactory.create(**deps)
    with pytest.raises(ValueError, match="Composition identifier must exist in composition_lookup"):
        RuntimeExecutionBuilderFactory.create("g", ident)

def test_validator_missing_descriptor_lookup(identity_deps):
    deps = dict(identity_deps)
    deps["descriptor_lookup"] = MappingProxyType({"other": identity_deps["descriptor"]})
    ident = ExecutionBuilderFactory.create(**deps)
    with pytest.raises(ValueError, match="Builder descriptor identifier must exist in descriptor_lookup"):
        RuntimeExecutionBuilderFactory.create("g", ident)

def test_validator_missing_snapshot_hash(identity_deps):
    deps = dict(identity_deps)
    snap_deps = {f.name: getattr(deps["snapshot"], f.name) for f in dataclasses.fields(deps["snapshot"])}
    snap_deps["builder_hash"] = ""
    deps["snapshot"] = RuntimeExecutionBuilderSnapshot(**snap_deps)
    ident = RuntimeExecutionBuilderIdentity(**deps)
    builder = RuntimeExecutionBuilder("g", ident)
    with pytest.raises(ValueError, match="Builder hash cannot be empty"):
        RuntimeExecutionBuilderValidator.validate(builder)

def test_builder_factory_returns_builder(identity_deps):
    ident = ExecutionBuilderFactory.create(**identity_deps)
    builder = RuntimeExecutionBuilderFactory.create("g", ident)
    assert isinstance(builder, RuntimeExecutionBuilder)

def test_builder_determinism(identity_deps):
    ident1 = ExecutionBuilderFactory.create(**identity_deps)
    builder1 = RuntimeExecutionBuilderFactory.create("g", ident1)
    
    ident2 = ExecutionBuilderFactory.create(**identity_deps)
    builder2 = RuntimeExecutionBuilderFactory.create("g", ident2)
    
    assert builder1 == builder2

def test_validator_no_execution_methods():
    assert not hasattr(RuntimeExecutionBuilderValidator, "execute")
    assert not hasattr(RuntimeExecutionBuilderValidator, "run")
