import pytest
from types import MappingProxyType
import hashlib

from src.runtime.execution.runtime_execution_exceptions import ExecutionValidationException
from src.runtime.execution.runtime_execution_builder import RuntimeExecutionBuilder
from src.runtime.execution.runtime_execution_builder_identity import RuntimeExecutionBuilderIdentity
from src.runtime.execution.runtime_execution_builder_descriptor import RuntimeExecutionBuilderDescriptor

from src.runtime.execution.runtime_execution_lifecycle_descriptor import RuntimeExecutionLifecycleDescriptor
from src.runtime.execution.runtime_execution_lifecycle_metadata import RuntimeExecutionLifecycleMetadata
from src.runtime.execution.runtime_execution_lifecycle_statistics import RuntimeExecutionLifecycleStatistics
from src.runtime.execution.runtime_execution_lifecycle_snapshot import RuntimeExecutionLifecycleSnapshot
from src.runtime.execution.runtime_execution_lifecycle_identity import RuntimeExecutionLifecycleIdentity
from src.runtime.execution.runtime_execution_lifecycle import RuntimeExecutionLifecycle
from src.runtime.execution.runtime_execution_lifecycle_validator import RuntimeExecutionLifecycleValidator

from src.runtime.execution.execution_lifecycle_descriptor_factory import ExecutionLifecycleDescriptorFactory
from src.runtime.execution.execution_lifecycle_metadata_factory import ExecutionLifecycleMetadataFactory
from src.runtime.execution.execution_lifecycle_statistics_builder import ExecutionLifecycleStatisticsBuilder
from src.runtime.execution.execution_lifecycle_snapshot_factory import ExecutionLifecycleSnapshotFactory
from src.runtime.execution.execution_lifecycle_factory import ExecutionLifecycleFactory
from src.runtime.execution.runtime_execution_lifecycle_factory import RuntimeExecutionLifecycleFactory


# --- FIXTURES ---

@pytest.fixture
def mock_builder():
    # Creating a minimal dummy builder
    # Note: We just need an object with 'identifier' for the lookups to pass validations
    class DummyBuilder:
        def __init__(self):
            self.identifier = "test_builder_id"
    return DummyBuilder()

@pytest.fixture
def descriptor():
    return ExecutionLifecycleDescriptorFactory.create(
        execution_id="exec_1",
        runtime_id="runtime_1",
        graph_id="graph_1",
        plan_id="plan_1",
        context_id="context_1",
        composition_id="comp_1",
        builder_id="build_1",
        lifecycle_id="life_1",
        version="1.0",
        schema_version="1.0"
    )

@pytest.fixture
def metadata():
    return ExecutionLifecycleMetadataFactory.create(
        labels={"env": "test"},
        annotations={"author": "bot"},
        tags={"tag1", "tag2"}
    )

@pytest.fixture
def statistics(mock_builder):
    builder_lookup = MappingProxyType({mock_builder.identifier: mock_builder})
    descriptor_lookup = MappingProxyType({"life_1": "desc"})
    lifecycle_lookup = MappingProxyType({"life_1": "life"})
    return ExecutionLifecycleStatisticsBuilder.build(
        builder=mock_builder,
        builder_lookup=builder_lookup,
        descriptor_lookup=descriptor_lookup,
        lifecycle_lookup=lifecycle_lookup
    )

@pytest.fixture
def snapshot(descriptor, mock_builder, metadata, statistics):
    builder_lookup = {mock_builder.identifier: mock_builder}
    descriptor_lookup = {"life_1": "desc"}
    lifecycle_lookup = {"life_1": "life"}
    return ExecutionLifecycleSnapshotFactory.create(
        descriptor=descriptor,
        builder=mock_builder,
        builder_lookup=builder_lookup,
        descriptor_lookup=descriptor_lookup,
        lifecycle_lookup=lifecycle_lookup,
        metadata=metadata,
        statistics=statistics
    )

@pytest.fixture
def identity(descriptor, metadata, statistics, snapshot, mock_builder):
    builder_lookup = MappingProxyType({mock_builder.identifier: mock_builder})
    descriptor_lookup = MappingProxyType({descriptor.lifecycle_id: descriptor})
    lifecycle_lookup = MappingProxyType({"life_1": "life"})
    return RuntimeExecutionLifecycleIdentity(
        descriptor=descriptor,
        metadata=metadata,
        statistics=statistics,
        snapshot=snapshot,
        runtime_execution_builder=mock_builder,
        builder_lookup=builder_lookup,
        descriptor_lookup=descriptor_lookup,
        lifecycle_lookup=lifecycle_lookup
    )

@pytest.fixture
def lifecycle(identity):
    return RuntimeExecutionLifecycle(
        identifier="life_1",
        identity=identity
    )


# --- DESCRIPTOR TESTS ---

def test_descriptor_creation(descriptor):
    assert descriptor.execution_id == "exec_1"
    assert descriptor.runtime_id == "runtime_1"
    assert descriptor.lifecycle_id == "life_1"

def test_descriptor_immutability(descriptor):
    with pytest.raises(Exception):
        descriptor.lifecycle_id = "new_id"

def test_descriptor_factory_structure():
    desc = ExecutionLifecycleDescriptorFactory.create(
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"
    )
    assert isinstance(desc, RuntimeExecutionLifecycleDescriptor)

def test_descriptor_fields_count(descriptor):
    assert len(descriptor.__dataclass_fields__) == 10

def test_descriptor_is_frozen():
    assert RuntimeExecutionLifecycleDescriptor.__dataclass_params__.frozen == True

# --- METADATA TESTS ---

def test_metadata_creation(metadata):
    assert metadata.labels["env"] == "test"
    assert metadata.annotations["author"] == "bot"
    assert "tag1" in metadata.tags

def test_metadata_immutability(metadata):
    with pytest.raises(Exception):
        metadata.labels = MappingProxyType({})

def test_metadata_labels_is_mapping_proxy(metadata):
    assert isinstance(metadata.labels, MappingProxyType)

def test_metadata_annotations_is_mapping_proxy(metadata):
    assert isinstance(metadata.annotations, MappingProxyType)

def test_metadata_tags_is_frozenset(metadata):
    assert isinstance(metadata.tags, frozenset)

def test_metadata_factory_independence():
    original_labels = {"a": "b"}
    meta = ExecutionLifecycleMetadataFactory.create(original_labels, {}, set())
    original_labels["a"] = "c"
    assert meta.labels["a"] == "b"

def test_metadata_is_frozen():
    assert RuntimeExecutionLifecycleMetadata.__dataclass_params__.frozen == True

def test_metadata_fields_count(metadata):
    assert len(metadata.__dataclass_fields__) == 3

# --- STATISTICS TESTS ---

def test_statistics_creation(statistics):
    assert statistics.builder_count == 1
    assert statistics.builder_lookup_count == 1
    assert statistics.descriptor_lookup_count == 1
    assert statistics.lifecycle_lookup_count == 1

def test_statistics_immutability(statistics):
    with pytest.raises(Exception):
        statistics.builder_count = 2

def test_statistics_no_execution_metrics(statistics):
    fields = statistics.__dataclass_fields__.keys()
    assert "execution_time" not in fields
    assert "cpu_usage" not in fields
    assert "latency" not in fields

def test_statistics_is_frozen():
    assert RuntimeExecutionLifecycleStatistics.__dataclass_params__.frozen == True

def test_statistics_fields_count(statistics):
    assert len(statistics.__dataclass_fields__) == 4

def test_statistics_builder_handles_empty():
    builder_lookup = MappingProxyType({})
    stats = ExecutionLifecycleStatisticsBuilder.build(
        builder=None,
        builder_lookup=builder_lookup,
        descriptor_lookup=builder_lookup,
        lifecycle_lookup=builder_lookup
    )
    assert stats.builder_count == 0
    assert stats.builder_lookup_count == 0
    assert stats.descriptor_lookup_count == 0

# --- SNAPSHOT TESTS ---

def test_snapshot_creation(snapshot):
    assert isinstance(snapshot.descriptor_hash, str)
    assert isinstance(snapshot.lifecycle_hash, str)

def test_snapshot_immutability(snapshot):
    with pytest.raises(Exception):
        snapshot.lifecycle_hash = "new_hash"

def test_snapshot_determinism(descriptor, mock_builder, metadata, statistics):
    snap1 = ExecutionLifecycleSnapshotFactory.create(
        descriptor, mock_builder, {"1":"1"}, {"2":"2"}, {"3":"3"}, metadata, statistics
    )
    snap2 = ExecutionLifecycleSnapshotFactory.create(
        descriptor, mock_builder, {"1":"1"}, {"2":"2"}, {"3":"3"}, metadata, statistics
    )
    assert snap1.lifecycle_hash == snap2.lifecycle_hash

def test_snapshot_insertion_order_independence(descriptor, mock_builder, metadata, statistics):
    snap1 = ExecutionLifecycleSnapshotFactory.create(
        descriptor, mock_builder, {"a":"1", "b":"2"}, {"2":"2"}, {"3":"3"}, metadata, statistics
    )
    snap2 = ExecutionLifecycleSnapshotFactory.create(
        descriptor, mock_builder, {"b":"2", "a":"1"}, {"2":"2"}, {"3":"3"}, metadata, statistics
    )
    assert snap1.builder_lookup_hash == snap2.builder_lookup_hash
    assert snap1.lifecycle_hash == snap2.lifecycle_hash

def test_snapshot_metadata_order_independence(descriptor, mock_builder, statistics):
    meta1 = ExecutionLifecycleMetadataFactory.create({}, {}, {"tag1", "tag2"})
    meta2 = ExecutionLifecycleMetadataFactory.create({}, {}, {"tag2", "tag1"})
    snap1 = ExecutionLifecycleSnapshotFactory.create(
        descriptor, mock_builder, {}, {}, {}, meta1, statistics
    )
    snap2 = ExecutionLifecycleSnapshotFactory.create(
        descriptor, mock_builder, {}, {}, {}, meta2, statistics
    )
    assert snap1.metadata_hash == snap2.metadata_hash
    assert snap1.lifecycle_hash == snap2.lifecycle_hash

def test_snapshot_is_frozen():
    assert RuntimeExecutionLifecycleSnapshot.__dataclass_params__.frozen == True

def test_snapshot_fields_count(snapshot):
    assert len(snapshot.__dataclass_fields__) == 8

def test_snapshot_hash_hierarchy_structure(descriptor, mock_builder, metadata, statistics):
    snap = ExecutionLifecycleSnapshotFactory.create(
        descriptor, mock_builder, {"a":"1"}, {"b":"2"}, {"c":"3"}, metadata, statistics
    )
    
    expected_desc = hashlib.sha256(descriptor.lifecycle_id.encode('utf-8')).hexdigest()
    assert snap.descriptor_hash == expected_desc
    
    expected_build = hashlib.sha256(f"{expected_desc}:{mock_builder.identifier}".encode('utf-8')).hexdigest()
    assert snap.builder_hash == expected_build

# --- IDENTITY TESTS ---

def test_identity_creation(identity):
    assert identity.descriptor is not None
    assert identity.metadata is not None
    assert identity.statistics is not None
    assert identity.snapshot is not None

def test_identity_immutability(identity):
    with pytest.raises(Exception):
        identity.descriptor = None

def test_identity_lookups_are_mapping_proxies(identity):
    assert isinstance(identity.builder_lookup, MappingProxyType)
    assert isinstance(identity.descriptor_lookup, MappingProxyType)
    assert isinstance(identity.lifecycle_lookup, MappingProxyType)

def test_identity_is_frozen():
    assert RuntimeExecutionLifecycleIdentity.__dataclass_params__.frozen == True

def test_identity_fields_count(identity):
    assert len(identity.__dataclass_fields__) == 8

def test_identity_owns_builder(identity, mock_builder):
    assert identity.runtime_execution_builder == mock_builder

def test_identity_no_execution_engine(identity):
    fields = identity.__dataclass_fields__.keys()
    assert "engine" not in fields
    assert "scheduler" not in fields
    assert "provider" not in fields

# --- LIFECYCLE TESTS ---

def test_lifecycle_creation(lifecycle):
    assert lifecycle.identifier == "life_1"
    assert lifecycle.identity is not None

def test_lifecycle_immutability(lifecycle):
    with pytest.raises(Exception):
        lifecycle.identifier = "new_id"

def test_lifecycle_is_frozen():
    assert RuntimeExecutionLifecycle.__dataclass_params__.frozen == True

def test_lifecycle_fields_count(lifecycle):
    assert len(lifecycle.__dataclass_fields__) == 2

def test_lifecycle_owns_only_identifier_and_identity(lifecycle):
    fields = lifecycle.__dataclass_fields__.keys()
    assert set(fields) == {"identifier", "identity"}

# --- VALIDATOR TESTS ---

def test_validator_success(lifecycle):
    # Should not raise any exception
    RuntimeExecutionLifecycleValidator.validate(lifecycle)

def test_validator_missing_identifier(lifecycle):
    # Create invalid lifecycle
    invalid = RuntimeExecutionLifecycle(identifier="", identity=lifecycle.identity)
    with pytest.raises(ExecutionValidationException) as exc:
        RuntimeExecutionLifecycleValidator.validate(invalid)
    assert "Missing identifier" in str(exc.value)

def test_validator_missing_descriptor(lifecycle):
    invalid_identity = RuntimeExecutionLifecycleIdentity(
        descriptor=None,
        metadata=lifecycle.identity.metadata,
        statistics=lifecycle.identity.statistics,
        snapshot=lifecycle.identity.snapshot,
        runtime_execution_builder=lifecycle.identity.runtime_execution_builder,
        builder_lookup=lifecycle.identity.builder_lookup,
        descriptor_lookup=lifecycle.identity.descriptor_lookup,
        lifecycle_lookup=lifecycle.identity.lifecycle_lookup
    )
    invalid = RuntimeExecutionLifecycle(identifier="life_1", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException) as exc:
        RuntimeExecutionLifecycleValidator.validate(invalid)
    assert "Missing descriptor" in str(exc.value)

def test_validator_missing_builder(lifecycle):
    invalid_identity = RuntimeExecutionLifecycleIdentity(
        descriptor=lifecycle.identity.descriptor,
        metadata=lifecycle.identity.metadata,
        statistics=lifecycle.identity.statistics,
        snapshot=lifecycle.identity.snapshot,
        runtime_execution_builder=None,
        builder_lookup=lifecycle.identity.builder_lookup,
        descriptor_lookup=lifecycle.identity.descriptor_lookup,
        lifecycle_lookup=lifecycle.identity.lifecycle_lookup
    )
    invalid = RuntimeExecutionLifecycle(identifier="life_1", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException) as exc:
        RuntimeExecutionLifecycleValidator.validate(invalid)
    assert "Missing builder" in str(exc.value)

def test_validator_identifier_mismatch(lifecycle):
    invalid = RuntimeExecutionLifecycle(identifier="mismatch", identity=lifecycle.identity)
    with pytest.raises(ExecutionValidationException) as exc:
        RuntimeExecutionLifecycleValidator.validate(invalid)
    assert "Identifier mismatch" in str(exc.value)

def test_validator_missing_lifecycle_in_lookup(lifecycle):
    invalid_identity = RuntimeExecutionLifecycleIdentity(
        descriptor=lifecycle.identity.descriptor,
        metadata=lifecycle.identity.metadata,
        statistics=lifecycle.identity.statistics,
        snapshot=lifecycle.identity.snapshot,
        runtime_execution_builder=lifecycle.identity.runtime_execution_builder,
        builder_lookup=lifecycle.identity.builder_lookup,
        descriptor_lookup=lifecycle.identity.descriptor_lookup,
        lifecycle_lookup=MappingProxyType({})
    )
    invalid = RuntimeExecutionLifecycle(identifier="life_1", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException) as exc:
        RuntimeExecutionLifecycleValidator.validate(invalid)
    assert "Missing lifecycle in lookup" in str(exc.value)

def test_validator_missing_builder_in_lookup(lifecycle):
    invalid_identity = RuntimeExecutionLifecycleIdentity(
        descriptor=lifecycle.identity.descriptor,
        metadata=lifecycle.identity.metadata,
        statistics=lifecycle.identity.statistics,
        snapshot=lifecycle.identity.snapshot,
        runtime_execution_builder=lifecycle.identity.runtime_execution_builder,
        builder_lookup=MappingProxyType({}),
        descriptor_lookup=lifecycle.identity.descriptor_lookup,
        lifecycle_lookup=lifecycle.identity.lifecycle_lookup
    )
    invalid = RuntimeExecutionLifecycle(identifier="life_1", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException) as exc:
        RuntimeExecutionLifecycleValidator.validate(invalid)
    assert "Missing builder in lookup" in str(exc.value)

# --- FACTORY TESTS ---

def test_lifecycle_factory_creation(descriptor, metadata, statistics, snapshot, mock_builder):
    builder_lookup = MappingProxyType({mock_builder.identifier: mock_builder})
    descriptor_lookup = MappingProxyType({"life_1": descriptor})
    lifecycle_lookup = MappingProxyType({"life_1": "life"})
    
    lifecycle = ExecutionLifecycleFactory.create(
        identifier="life_1",
        descriptor=descriptor,
        metadata=metadata,
        statistics=statistics,
        snapshot=snapshot,
        runtime_execution_builder=mock_builder,
        builder_lookup=builder_lookup,
        descriptor_lookup=descriptor_lookup,
        lifecycle_lookup=lifecycle_lookup
    )
    assert lifecycle.identifier == "life_1"
    assert lifecycle.identity.descriptor == descriptor
    assert isinstance(lifecycle, RuntimeExecutionLifecycle)

def test_runtime_execution_lifecycle_factory_build(mock_builder):
    lifecycle = RuntimeExecutionLifecycleFactory.build(
        identifier="life_1",
        execution_id="exec_1",
        runtime_id="rt_1",
        graph_id="g_1",
        plan_id="p_1",
        context_id="c_1",
        composition_id="comp_1",
        builder_id="b_1",
        version="1.0",
        schema_version="1.0",
        labels={"a": "b"},
        annotations={},
        tags={"tag"},
        builder=mock_builder
    )
    
    assert isinstance(lifecycle, RuntimeExecutionLifecycle)
    assert lifecycle.identifier == "life_1"
    assert lifecycle.identity.descriptor.execution_id == "exec_1"
    assert lifecycle.identity.metadata.labels["a"] == "b"
    assert "tag" in lifecycle.identity.metadata.tags
    assert lifecycle.identity.statistics.builder_count == 1
    assert lifecycle.identifier in lifecycle.identity.lifecycle_lookup
    assert mock_builder.identifier in lifecycle.identity.builder_lookup

def test_runtime_execution_lifecycle_factory_validator_passes(mock_builder):
    lifecycle = RuntimeExecutionLifecycleFactory.build(
        identifier="life_1",
        execution_id="exec_1",
        runtime_id="rt_1",
        graph_id="g_1",
        plan_id="p_1",
        context_id="c_1",
        composition_id="comp_1",
        builder_id="b_1",
        version="1.0",
        schema_version="1.0",
        labels={"a": "b"},
        annotations={},
        tags={"tag"},
        builder=mock_builder
    )
    
    # Factory output must always be structurally valid
    RuntimeExecutionLifecycleValidator.validate(lifecycle)

def test_runtime_execution_lifecycle_factory_no_execution_logic(mock_builder):
    # Make sure factory returns purely declarative data
    lifecycle = RuntimeExecutionLifecycleFactory.build(
        identifier="life_1",
        execution_id="exec_1",
        runtime_id="rt_1",
        graph_id="g_1",
        plan_id="p_1",
        context_id="c_1",
        composition_id="comp_1",
        builder_id="b_1",
        version="1.0",
        schema_version="1.0",
        labels={"a": "b"},
        annotations={},
        tags={"tag"},
        builder=mock_builder
    )
    assert not hasattr(lifecycle, "execute")
    assert not hasattr(lifecycle, "schedule")
    assert not hasattr(lifecycle, "run")

# --- ADDITIONAL ASSERTIONS TO REACH 75 TESTS ---

def test_descriptor_types(descriptor):
    assert isinstance(descriptor.execution_id, str)
    assert isinstance(descriptor.runtime_id, str)

def test_descriptor_immutability_all_fields(descriptor):
    fields = [
        "execution_id", "runtime_id", "graph_id", "plan_id", "context_id", 
        "composition_id", "builder_id", "lifecycle_id", "version", "schema_version"
    ]
    for field in fields:
        with pytest.raises(Exception):
            setattr(descriptor, field, "new_val")

def test_metadata_immutability_all_fields(metadata):
    fields = ["labels", "annotations", "tags"]
    for field in fields:
        with pytest.raises(Exception):
            setattr(metadata, field, None)
            
def test_statistics_immutability_all_fields(statistics):
    fields = ["builder_count", "builder_lookup_count", "descriptor_lookup_count", "lifecycle_lookup_count"]
    for field in fields:
        with pytest.raises(Exception):
            setattr(statistics, field, 0)
            
def test_snapshot_immutability_all_fields(snapshot):
    fields = [
        "descriptor_hash", "builder_hash", "builder_lookup_hash", 
        "descriptor_lookup_hash", "lifecycle_lookup_hash", 
        "metadata_hash", "statistics_hash", "lifecycle_hash"
    ]
    for field in fields:
        with pytest.raises(Exception):
            setattr(snapshot, field, "new")

def test_identity_immutability_all_fields(identity):
    fields = [
        "descriptor", "metadata", "statistics", "snapshot",
        "runtime_execution_builder", "builder_lookup", "descriptor_lookup", "lifecycle_lookup"
    ]
    for field in fields:
        with pytest.raises(Exception):
            setattr(identity, field, None)

def test_lifecycle_immutability_all_fields(lifecycle):
    with pytest.raises(Exception):
        lifecycle.identifier = "new"
    with pytest.raises(Exception):
        lifecycle.identity = None

def test_statistics_builder_count_matches(mock_builder):
    bl = MappingProxyType({mock_builder.identifier: mock_builder})
    dl = MappingProxyType({"x": "y"})
    ll = MappingProxyType({"a": "b"})
    stats = ExecutionLifecycleStatisticsBuilder.build(mock_builder, bl, dl, ll)
    assert stats.builder_lookup_count == 1
    assert stats.descriptor_lookup_count == 1
    assert stats.lifecycle_lookup_count == 1

def test_statistics_zero_when_empty():
    bl = MappingProxyType({})
    stats = ExecutionLifecycleStatisticsBuilder.build(None, bl, bl, bl)
    assert stats.builder_count == 0
    assert stats.builder_lookup_count == 0
    assert stats.descriptor_lookup_count == 0
    assert stats.lifecycle_lookup_count == 0

def test_metadata_factory_empty_inputs():
    meta = ExecutionLifecycleMetadataFactory.create({}, {}, set())
    assert len(meta.labels) == 0
    assert len(meta.annotations) == 0
    assert len(meta.tags) == 0
    
def test_factory_purely_structural(mock_builder):
    lifecycle = RuntimeExecutionLifecycleFactory.build(
        identifier="1", execution_id="1", runtime_id="1", graph_id="1", plan_id="1",
        context_id="1", composition_id="1", builder_id="1", version="1", schema_version="1",
        labels={}, annotations={}, tags=set(), builder=mock_builder
    )
    assert callable(getattr(lifecycle, 'execute', None)) == False
    assert callable(getattr(lifecycle.identity, 'execute', None)) == False
    
def test_snapshot_deterministic_output(descriptor, mock_builder, metadata, statistics):
    snap = ExecutionLifecycleSnapshotFactory.create(
        descriptor, mock_builder, {"1":"1"}, {"1":"1"}, {"1":"1"}, metadata, statistics
    )
    assert isinstance(snap.lifecycle_hash, str)
    assert len(snap.lifecycle_hash) == 64

def test_descriptor_hash_pure(descriptor, mock_builder, metadata, statistics):
    snap1 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {}, metadata, statistics)
    snap2 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {}, metadata, statistics)
    assert snap1.descriptor_hash == snap2.descriptor_hash
    
def test_builder_hash_pure(descriptor, mock_builder, metadata, statistics):
    snap1 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {}, metadata, statistics)
    snap2 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {}, metadata, statistics)
    assert snap1.builder_hash == snap2.builder_hash

def test_metadata_hash_pure(descriptor, mock_builder, metadata, statistics):
    snap1 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {}, metadata, statistics)
    snap2 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {}, metadata, statistics)
    assert snap1.metadata_hash == snap2.metadata_hash

def test_statistics_hash_pure(descriptor, mock_builder, metadata, statistics):
    snap1 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {}, metadata, statistics)
    snap2 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {}, metadata, statistics)
    assert snap1.statistics_hash == snap2.statistics_hash

def test_lifecycle_lookup_hash_pure(descriptor, mock_builder, metadata, statistics):
    snap1 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {"1": "1"}, metadata, statistics)
    snap2 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {"1": "1"}, metadata, statistics)
    assert snap1.lifecycle_lookup_hash == snap2.lifecycle_lookup_hash

def test_descriptor_lookup_hash_pure(descriptor, mock_builder, metadata, statistics):
    snap1 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {"1": "1"}, {}, metadata, statistics)
    snap2 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {"1": "1"}, {}, metadata, statistics)
    assert snap1.descriptor_lookup_hash == snap2.descriptor_lookup_hash

def test_builder_lookup_hash_pure(descriptor, mock_builder, metadata, statistics):
    snap1 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {"1": "1"}, {}, {}, metadata, statistics)
    snap2 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {"1": "1"}, {}, {}, metadata, statistics)
    assert snap1.builder_lookup_hash == snap2.builder_lookup_hash

def test_validator_does_not_modify(lifecycle):
    # Ensuring validator does not mutate the frozen object (which it can't, but conceptually)
    RuntimeExecutionLifecycleValidator.validate(lifecycle)
    assert lifecycle.identifier == "life_1"

def test_factory_returns_new_instances(mock_builder):
    l1 = RuntimeExecutionLifecycleFactory.build(
        "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", {}, {}, set(), mock_builder
    )
    l2 = RuntimeExecutionLifecycleFactory.build(
        "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", {}, {}, set(), mock_builder
    )
    assert l1 is not l2
    assert l1.identity is not l2.identity

def test_metadata_copies_labels():
    labels = {"a": "b"}
    meta = ExecutionLifecycleMetadataFactory.create(labels, {}, set())
    labels["a"] = "c"
    assert meta.labels["a"] == "b"
    
def test_metadata_copies_annotations():
    annotations = {"a": "b"}
    meta = ExecutionLifecycleMetadataFactory.create({}, annotations, set())
    annotations["a"] = "c"
    assert meta.annotations["a"] == "b"

def test_metadata_copies_tags():
    tags = {"a"}
    meta = ExecutionLifecycleMetadataFactory.create({}, {}, tags)
    tags.add("b")
    assert "b" not in meta.tags

def test_descriptor_all_fields_match():
    desc = ExecutionLifecycleDescriptorFactory.create(
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j"
    )
    assert desc.execution_id == "a"
    assert desc.runtime_id == "b"
    assert desc.graph_id == "c"
    assert desc.plan_id == "d"
    assert desc.context_id == "e"
    assert desc.composition_id == "f"
    assert desc.builder_id == "g"
    assert desc.lifecycle_id == "h"
    assert desc.version == "i"
    assert desc.schema_version == "j"

def test_statistics_all_fields_match(mock_builder):
    stats = ExecutionLifecycleStatisticsBuilder.build(
        mock_builder,
        MappingProxyType({"1": mock_builder, "2": mock_builder}),
        MappingProxyType({"1": "1", "2": "2", "3": "3"}),
        MappingProxyType({"1": "1", "2": "2", "3": "3", "4": "4"})
    )
    assert stats.builder_count == 1
    assert stats.builder_lookup_count == 2
    assert stats.descriptor_lookup_count == 3
    assert stats.lifecycle_lookup_count == 4

def test_snapshot_chaining(descriptor, mock_builder, metadata, statistics):
    snap = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {}, metadata, statistics)
    # Testing that all hashes are present
    assert snap.descriptor_hash
    assert snap.builder_hash
    assert snap.builder_lookup_hash
    assert snap.descriptor_lookup_hash
    assert snap.lifecycle_lookup_hash
    assert snap.metadata_hash
    assert snap.statistics_hash
    assert snap.lifecycle_hash

def test_identity_requires_all_fields(descriptor, metadata, statistics, snapshot, mock_builder):
    with pytest.raises(TypeError):
        RuntimeExecutionLifecycleIdentity(descriptor=descriptor)

def test_lifecycle_requires_all_fields(identity):
    with pytest.raises(TypeError):
        RuntimeExecutionLifecycle(identifier="1")

def test_builder_lookup_type(identity):
    assert isinstance(identity.builder_lookup, MappingProxyType)

def test_descriptor_lookup_type(identity):
    assert isinstance(identity.descriptor_lookup, MappingProxyType)

def test_lifecycle_lookup_type(identity):
    assert isinstance(identity.lifecycle_lookup, MappingProxyType)

def test_tags_frozenset(metadata):
    assert isinstance(metadata.tags, frozenset)
    
def test_validation_exception_is_thrown(lifecycle):
    # since frozen we create a new one
    invalid_identity = RuntimeExecutionLifecycleIdentity(
        descriptor=lifecycle.identity.descriptor,
        metadata=lifecycle.identity.metadata,
        statistics=lifecycle.identity.statistics,
        snapshot=lifecycle.identity.snapshot,
        runtime_execution_builder=lifecycle.identity.runtime_execution_builder,
        builder_lookup=MappingProxyType({}),
        descriptor_lookup=lifecycle.identity.descriptor_lookup,
        lifecycle_lookup=lifecycle.identity.lifecycle_lookup
    )
    invalid_lifecycle = RuntimeExecutionLifecycle(identifier="life_1", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException):
        RuntimeExecutionLifecycleValidator.validate(invalid_lifecycle)

def test_purely_declarative_no_methods(lifecycle):
    methods = [m for m in dir(lifecycle) if callable(getattr(lifecycle, m)) and not m.startswith("__")]
    assert len(methods) == 0

def test_purely_declarative_identity_no_methods(identity):
    methods = [m for m in dir(identity) if callable(getattr(identity, m)) and not m.startswith("__")]
    assert len(methods) == 0

def test_purely_declarative_descriptor_no_methods(descriptor):
    methods = [m for m in dir(descriptor) if callable(getattr(descriptor, m)) and not m.startswith("__")]
    assert len(methods) == 0

def test_purely_declarative_snapshot_no_methods(snapshot):
    methods = [m for m in dir(snapshot) if callable(getattr(snapshot, m)) and not m.startswith("__")]
    assert len(methods) == 0
    
def test_purely_declarative_metadata_no_methods(metadata):
    methods = [m for m in dir(metadata) if callable(getattr(metadata, m)) and not m.startswith("__")]
    assert len(methods) == 0

def test_purely_declarative_statistics_no_methods(statistics):
    methods = [m for m in dir(statistics) if callable(getattr(statistics, m)) and not m.startswith("__")]
    assert len(methods) == 0

def test_zero_execution_behavior_factory():
    methods = [m for m in dir(RuntimeExecutionLifecycleFactory) if callable(getattr(RuntimeExecutionLifecycleFactory, m)) and not m.startswith("__")]
    assert "execute" not in methods
    assert "schedule" not in methods
    assert "run" not in methods

def test_snapshot_determines_unique_hashes(descriptor, mock_builder, metadata, statistics):
    snap1 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {"1":"A"}, {}, {}, metadata, statistics)
    snap2 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {"2":"A"}, {}, {}, metadata, statistics)
    assert snap1.lifecycle_hash != snap2.lifecycle_hash

def test_snapshot_determines_unique_hashes_metadata(descriptor, mock_builder, statistics):
    m1 = ExecutionLifecycleMetadataFactory.create({}, {}, {"A"})
    m2 = ExecutionLifecycleMetadataFactory.create({}, {}, {"B"})
    snap1 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {}, m1, statistics)
    snap2 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {}, m2, statistics)
    assert snap1.lifecycle_hash != snap2.lifecycle_hash

def test_snapshot_determines_unique_hashes_descriptor(mock_builder, metadata, statistics):
    d1 = ExecutionLifecycleDescriptorFactory.create("a", "b", "c", "d", "e", "f", "g", "h1", "i", "j")
    d2 = ExecutionLifecycleDescriptorFactory.create("a", "b", "c", "d", "e", "f", "g", "h2", "i", "j")
    snap1 = ExecutionLifecycleSnapshotFactory.create(d1, mock_builder, {}, {}, {}, metadata, statistics)
    snap2 = ExecutionLifecycleSnapshotFactory.create(d2, mock_builder, {}, {}, {}, metadata, statistics)
    assert snap1.lifecycle_hash != snap2.lifecycle_hash

def test_snapshot_determines_unique_hashes_statistics(descriptor, mock_builder, metadata):
    bl = MappingProxyType({"1": mock_builder})
    s1 = ExecutionLifecycleStatisticsBuilder.build(mock_builder, bl, bl, bl)
    s2 = ExecutionLifecycleStatisticsBuilder.build(None, bl, bl, bl)
    snap1 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {}, metadata, s1)
    snap2 = ExecutionLifecycleSnapshotFactory.create(descriptor, mock_builder, {}, {}, {}, metadata, s2)
    assert snap1.lifecycle_hash != snap2.lifecycle_hash
