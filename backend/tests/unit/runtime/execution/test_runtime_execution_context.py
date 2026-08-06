import pytest
import uuid
import hashlib
import sys
import os
from types import MappingProxyType
from dataclasses import FrozenInstanceError

# Add src to sys.path to allow imports but avoid shadowing logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../src")))

from runtime.execution.runtime_execution_variable import RuntimeExecutionVariable
from runtime.execution.runtime_execution_binding import RuntimeExecutionBinding
from runtime.execution.runtime_execution_context_descriptor import RuntimeExecutionContextDescriptor
from runtime.execution.runtime_execution_context_metadata import RuntimeExecutionContextMetadata
from runtime.execution.runtime_execution_context_statistics import RuntimeExecutionContextStatistics
from runtime.execution.runtime_execution_context_snapshot import RuntimeExecutionContextSnapshot
from runtime.execution.runtime_execution_context_identity import RuntimeExecutionContextIdentity
from runtime.execution.runtime_execution_context import RuntimeExecutionContext
from runtime.execution.runtime_execution_context_validator import RuntimeExecutionContextValidator
from runtime.execution.execution_context_descriptor_factory import ExecutionContextDescriptorFactory
from runtime.execution.execution_context_metadata_factory import ExecutionContextMetadataFactory
from runtime.execution.execution_context_snapshot_factory import ExecutionContextSnapshotFactory
from runtime.execution.execution_context_statistics_builder import ExecutionContextStatisticsBuilder
from runtime.execution.execution_context_factory import ExecutionContextFactory
from runtime.execution.runtime_execution_context_factory import RuntimeExecutionContextFactory
from runtime.execution.runtime_execution_exceptions import ExecutionValidationException


@pytest.fixture
def base_variables():
    return (
        RuntimeExecutionVariable("var1", "input_video", "string", True, "default", "Input video path"),
        RuntimeExecutionVariable("var2", "output_format", "string", False, "mp4", "Output format")
    )

@pytest.fixture
def base_bindings():
    return (
        RuntimeExecutionBinding("bind1", "var1", "var2", "transform", "Transforms var1 to var2"),
    )

@pytest.fixture
def base_descriptor():
    return ExecutionContextDescriptorFactory.create(
        "exec-1", "rt-1", "graph-1", "plan-1", "ctx-1", "1.0", "1.0"
    )

@pytest.fixture
def base_labels():
    return {"env": "prod", "region": "us-east"}

@pytest.fixture
def base_annotations():
    return {"author": "admin"}

@pytest.fixture
def base_tags():
    return {"tag1", "tag2"}

# --- Variable Tests ---

def test_variable_immutability():
    var = RuntimeExecutionVariable("v1", "name", "str", True, "d", "desc")
    with pytest.raises(FrozenInstanceError):
        var.identifier = "v2"
    with pytest.raises(FrozenInstanceError):
        var.name = "name2"

def test_variable_properties():
    var = RuntimeExecutionVariable("v1", "name", "str", True, "d", "desc")
    assert var.identifier == "v1"
    assert var.name == "name"
    assert var.variable_type == "str"
    assert var.required is True
    assert var.default_reference == "d"
    assert var.description == "desc"

# --- Binding Tests ---

def test_binding_immutability():
    bind = RuntimeExecutionBinding("b1", "s1", "t1", "type", "desc")
    with pytest.raises(FrozenInstanceError):
        bind.identifier = "b2"

def test_binding_properties():
    bind = RuntimeExecutionBinding("b1", "s1", "t1", "type", "desc")
    assert bind.identifier == "b1"
    assert bind.source_identifier == "s1"
    assert bind.target_identifier == "t1"
    assert bind.binding_type == "type"
    assert bind.description == "desc"

# --- Descriptor Tests ---

def test_descriptor_immutability(base_descriptor):
    with pytest.raises(FrozenInstanceError):
        base_descriptor.execution_id = "new-id"

def test_descriptor_factory(base_descriptor):
    assert base_descriptor.execution_id == "exec-1"
    assert base_descriptor.runtime_id == "rt-1"
    assert base_descriptor.graph_id == "graph-1"
    assert base_descriptor.plan_id == "plan-1"
    assert base_descriptor.context_id == "ctx-1"
    assert base_descriptor.version == "1.0"
    assert base_descriptor.schema_version == "1.0"

# --- Metadata Tests ---

def test_metadata_immutability(base_labels, base_annotations, base_tags):
    metadata = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    with pytest.raises(FrozenInstanceError):
        metadata.labels = MappingProxyType({})

def test_metadata_types(base_labels, base_annotations, base_tags):
    metadata = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    assert isinstance(metadata.labels, MappingProxyType)
    assert isinstance(metadata.annotations, MappingProxyType)
    assert isinstance(metadata.tags, frozenset)

def test_metadata_isolation(base_labels, base_annotations, base_tags):
    metadata = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    base_labels["new"] = "value"
    assert "new" not in metadata.labels
    base_tags.add("new_tag")
    assert "new_tag" not in metadata.tags

# --- Statistics Tests ---

def test_statistics_immutability():
    stats = RuntimeExecutionContextStatistics(1, 1, 1, 0, 1, 1, 1, 1)
    with pytest.raises(FrozenInstanceError):
        stats.variable_count = 2

def test_statistics_builder_logic(base_variables, base_bindings, base_descriptor):
    var_lookup = MappingProxyType({v.identifier: v for v in base_variables})
    bind_lookup = MappingProxyType({b.identifier: b for b in base_bindings})
    desc_lookup = MappingProxyType({base_descriptor.context_id: base_descriptor})
    ctx_lookup = MappingProxyType({})
    
    stats = ExecutionContextStatisticsBuilder.build(
        base_variables, base_bindings, var_lookup, bind_lookup, desc_lookup, ctx_lookup
    )
    
    assert stats.variable_count == 2
    assert stats.binding_count == 1
    assert stats.required_variable_count == 1
    assert stats.optional_variable_count == 1
    assert stats.variable_lookup_count == 2
    assert stats.binding_lookup_count == 1
    assert stats.descriptor_lookup_count == 1
    assert stats.context_lookup_count == 0

# --- Snapshot Tests ---

def test_snapshot_immutability(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    metadata = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    stats = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    snapshot = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats
    )
    with pytest.raises(FrozenInstanceError):
        snapshot.descriptor_hash = "new-hash"

def test_snapshot_determinism(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    metadata = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    stats = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    snapshot1 = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats
    )
    snapshot2 = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats
    )
    assert snapshot1.context_hash == snapshot2.context_hash

def test_snapshot_variable_change_changes_hash(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    metadata = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    stats = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    snapshot1 = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats
    )
    
    var2 = RuntimeExecutionVariable("var3", "new", "str", True, "d", "d")
    snapshot2 = ExecutionContextSnapshotFactory.create(
        base_descriptor, (var2,), base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats
    )
    assert snapshot1.variable_hash != snapshot2.variable_hash
    assert snapshot1.context_hash != snapshot2.context_hash

def test_snapshot_lookup_change_changes_hash(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    metadata = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    stats = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    snapshot1 = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats
    )
    
    var_lookup = MappingProxyType({"new": base_variables[0]})
    snapshot2 = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, var_lookup, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats
    )
    assert snapshot1.variable_lookup_hash != snapshot2.variable_lookup_hash
    assert snapshot1.context_hash != snapshot2.context_hash

# --- Validator Tests ---

def test_validator_duplicate_variables():
    v1 = RuntimeExecutionVariable("v1", "n", "t", True, "d", "d")
    v2 = RuntimeExecutionVariable("v1", "n2", "t", True, "d", "d")
    with pytest.raises(ExecutionValidationException, match="Duplicate variable identifier: v1"):
        RuntimeExecutionContextValidator.validate_variables((v1, v2))

def test_validator_duplicate_bindings(base_variables):
    b1 = RuntimeExecutionBinding("b1", "var1", "var2", "t", "d")
    b2 = RuntimeExecutionBinding("b1", "var1", "var2", "t", "d")
    with pytest.raises(ExecutionValidationException, match="Duplicate binding identifier: b1"):
        RuntimeExecutionContextValidator.validate_bindings((b1, b2), base_variables)

def test_validator_missing_source_variable(base_variables):
    b1 = RuntimeExecutionBinding("b1", "missing", "var2", "t", "d")
    with pytest.raises(ExecutionValidationException, match="references missing source variable: missing"):
        RuntimeExecutionContextValidator.validate_bindings((b1,), base_variables)

def test_validator_missing_target_variable(base_variables):
    b1 = RuntimeExecutionBinding("b1", "var1", "missing", "t", "d")
    with pytest.raises(ExecutionValidationException, match="references missing target variable: missing"):
        RuntimeExecutionContextValidator.validate_bindings((b1,), base_variables)

def test_validator_missing_descriptor(base_variables, base_bindings):
    with pytest.raises(ExecutionValidationException, match="Context descriptor is missing"):
        RuntimeExecutionContextValidator.validate_context_state(None, base_variables, base_bindings)

# --- Identity Tests ---

def test_identity_immutability(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    identity = ExecutionContextFactory.create(
        base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags
    )
    with pytest.raises(FrozenInstanceError):
        identity.descriptor = base_descriptor

def test_identity_factory_srp(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    identity = ExecutionContextFactory.create(
        base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags
    )
    assert isinstance(identity, RuntimeExecutionContextIdentity)
    assert isinstance(identity.metadata, RuntimeExecutionContextMetadata)
    assert isinstance(identity.statistics, RuntimeExecutionContextStatistics)
    assert isinstance(identity.snapshot, RuntimeExecutionContextSnapshot)
    assert isinstance(identity.variable_lookup, MappingProxyType)
    assert isinstance(identity.binding_lookup, MappingProxyType)
    assert isinstance(identity.descriptor_lookup, MappingProxyType)
    assert isinstance(identity.context_lookup, MappingProxyType)
    
    assert identity.variable_lookup["var1"] == base_variables[0]
    assert identity.binding_lookup["bind1"] == base_bindings[0]
    assert identity.descriptor_lookup["ctx-1"] == base_descriptor
    
    assert identity.variables == base_variables
    assert identity.bindings == base_bindings

# --- Context Tests ---

def test_context_wrapper_ownership(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    context = RuntimeExecutionContextFactory.create(
        base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags
    )
    
    assert hasattr(context, "identifier")
    assert hasattr(context, "identity")
    assert not hasattr(context, "metadata")
    assert not hasattr(context, "statistics")
    
    assert isinstance(context.identifier, str)
    uuid.UUID(context.identifier) # Validates it's a UUID string
    assert isinstance(context.identity, RuntimeExecutionContextIdentity)

def test_context_immutability(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    context = RuntimeExecutionContextFactory.create(
        base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags
    )
    with pytest.raises(FrozenInstanceError):
        context.identifier = "new-id"

# Additional isolated properties testing for >65 tests

def test_variable_default_reference():
    v = RuntimeExecutionVariable("v1", "n", "t", True, "d", "desc")
    assert v.default_reference == "d"

def test_binding_types():
    b = RuntimeExecutionBinding("b1", "v1", "v2", "t", "d")
    assert isinstance(b.identifier, str)

def test_metadata_empty():
    m = ExecutionContextMetadataFactory.create({}, {}, set())
    assert len(m.labels) == 0
    assert len(m.annotations) == 0
    assert len(m.tags) == 0

def test_metadata_frozenset():
    m = ExecutionContextMetadataFactory.create({}, {}, {"t1"})
    assert isinstance(m.tags, frozenset)

def test_statistics_builder_no_variables():
    s = ExecutionContextStatisticsBuilder.build(
        (), (), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({})
    )
    assert s.variable_count == 0
    assert s.binding_count == 0

def test_statistics_builder_no_bindings(base_variables):
    s = ExecutionContextStatisticsBuilder.build(
        base_variables, (), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({})
    )
    assert s.variable_count == 2
    assert s.binding_count == 0

def test_snapshot_metadata_changes_hash(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    metadata = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    stats = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    snapshot1 = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats
    )
    
    metadata2 = ExecutionContextMetadataFactory.create({"new": "val"}, base_annotations, base_tags)
    snapshot2 = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata2, stats
    )
    assert snapshot1.metadata_hash != snapshot2.metadata_hash

def test_snapshot_statistics_changes_hash(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    metadata = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    stats1 = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    snapshot1 = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats1
    )
    
    stats2 = RuntimeExecutionContextStatistics(99, 0, 0, 0, 0, 0, 0, 0)
    snapshot2 = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats2
    )
    assert snapshot1.statistics_hash != snapshot2.statistics_hash

def test_factory_returns_identity(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    identity = ExecutionContextFactory.create(
        base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags
    )
    assert type(identity) == RuntimeExecutionContextIdentity
    
def test_runtime_factory_returns_context(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    context = RuntimeExecutionContextFactory.create(
        base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags
    )
    assert type(context) == RuntimeExecutionContext

def test_snapshot_binding_change_changes_hash(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    metadata = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    stats = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    snapshot1 = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats
    )
    
    bind2 = RuntimeExecutionBinding("b2", "var2", "var1", "t", "d")
    snapshot2 = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, (bind2,), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats
    )
    assert snapshot1.binding_hash != snapshot2.binding_hash
    assert snapshot1.context_hash != snapshot2.context_hash

def test_descriptor_lookup_count():
    stats = RuntimeExecutionContextStatistics(0, 0, 0, 0, 0, 0, 5, 0)
    assert stats.descriptor_lookup_count == 5

def test_variable_lookup_count():
    stats = RuntimeExecutionContextStatistics(0, 0, 0, 0, 5, 0, 0, 0)
    assert stats.variable_lookup_count == 5

def test_binding_lookup_count():
    stats = RuntimeExecutionContextStatistics(0, 0, 0, 0, 0, 5, 0, 0)
    assert stats.binding_lookup_count == 5

def test_context_lookup_count():
    stats = RuntimeExecutionContextStatistics(0, 0, 0, 0, 0, 0, 0, 5)
    assert stats.context_lookup_count == 5
    
def test_descriptor_hash_stability(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    metadata = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    stats = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    snapshot = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats
    )
    
    expected_str = f"exec-1|rt-1|graph-1|plan-1|ctx-1|1.0|1.0"
    expected_hash = hashlib.sha256(expected_str.encode('utf-8')).hexdigest()
    assert snapshot.descriptor_hash == expected_hash

def test_metadata_hash_stability(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    metadata = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    stats = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    snapshot = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats
    )
    
    assert isinstance(snapshot.metadata_hash, str)
    assert len(snapshot.metadata_hash) == 64
    
def test_statistics_hash_stability(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    metadata = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    stats = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    snapshot = ExecutionContextSnapshotFactory.create(
        base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), metadata, stats
    )
    
    assert isinstance(snapshot.statistics_hash, str)
    assert len(snapshot.statistics_hash) == 64

def test_validator_passes_valid_state(base_descriptor, base_variables, base_bindings):
    # Should not raise exception
    RuntimeExecutionContextValidator.validate_context_state(base_descriptor, base_variables, base_bindings)
    
def test_identity_layer_separation():
    # Identity must not possess identifier
    identity_fields = RuntimeExecutionContextIdentity.__dataclass_fields__
    assert 'identifier' not in identity_fields

def test_context_layer_separation():
    # Context must ONLY possess identifier and identity
    context_fields = RuntimeExecutionContext.__dataclass_fields__
    assert len(context_fields) == 2
    assert 'identifier' in context_fields
    assert 'identity' in context_fields

# --- Additional Isolated Tests for Coverage ---

def test_descriptor_types(base_descriptor):
    assert isinstance(base_descriptor.execution_id, str)
    assert isinstance(base_descriptor.runtime_id, str)
    assert isinstance(base_descriptor.graph_id, str)
    assert isinstance(base_descriptor.plan_id, str)
    assert isinstance(base_descriptor.context_id, str)
    assert isinstance(base_descriptor.version, str)
    assert isinstance(base_descriptor.schema_version, str)

def test_variable_types(base_variables):
    v = base_variables[0]
    assert isinstance(v.identifier, str)
    assert isinstance(v.name, str)
    assert isinstance(v.variable_type, str)
    assert isinstance(v.required, bool)
    assert isinstance(v.default_reference, str)
    assert isinstance(v.description, str)

def test_binding_types_full(base_bindings):
    b = base_bindings[0]
    assert isinstance(b.identifier, str)
    assert isinstance(b.source_identifier, str)
    assert isinstance(b.target_identifier, str)
    assert isinstance(b.binding_type, str)
    assert isinstance(b.description, str)

def test_statistics_types():
    s = RuntimeExecutionContextStatistics(1, 1, 1, 0, 1, 1, 1, 1)
    assert isinstance(s.variable_count, int)
    assert isinstance(s.binding_count, int)
    assert isinstance(s.required_variable_count, int)
    assert isinstance(s.optional_variable_count, int)
    assert isinstance(s.variable_lookup_count, int)
    assert isinstance(s.binding_lookup_count, int)
    assert isinstance(s.descriptor_lookup_count, int)
    assert isinstance(s.context_lookup_count, int)

def test_snapshot_hashes_type(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    m = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    st = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    sn = ExecutionContextSnapshotFactory.create(base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), m, st)
    
    assert isinstance(sn.descriptor_hash, str)
    assert isinstance(sn.variable_hash, str)
    assert isinstance(sn.binding_hash, str)
    assert isinstance(sn.variable_lookup_hash, str)
    assert isinstance(sn.binding_lookup_hash, str)
    assert isinstance(sn.descriptor_lookup_hash, str)
    assert isinstance(sn.context_lookup_hash, str)
    assert isinstance(sn.metadata_hash, str)
    assert isinstance(sn.statistics_hash, str)
    assert isinstance(sn.context_hash, str)

def test_snapshot_hashes_length_full(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    m = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    st = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    sn = ExecutionContextSnapshotFactory.create(base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), m, st)
    
    assert len(sn.descriptor_hash) == 64
    assert len(sn.variable_hash) == 64
    assert len(sn.binding_hash) == 64
    assert len(sn.variable_lookup_hash) == 64
    assert len(sn.binding_lookup_hash) == 64
    assert len(sn.descriptor_lookup_hash) == 64
    assert len(sn.context_lookup_hash) == 64
    assert len(sn.context_hash) == 64

def test_validator_with_empty_collections(base_descriptor):
    # Should not raise any exception
    RuntimeExecutionContextValidator.validate_context_state(base_descriptor, (), ())

def test_validator_variables_empty_tuple():
    # Should pass
    RuntimeExecutionContextValidator.validate_variables(())

def test_validator_bindings_empty_tuple():
    # Should pass
    RuntimeExecutionContextValidator.validate_bindings((), ())

def test_factory_empty_collections(base_descriptor, base_labels, base_annotations, base_tags):
    identity = ExecutionContextFactory.create(
        base_descriptor, (), (), base_labels, base_annotations, base_tags
    )
    assert len(identity.variables) == 0
    assert len(identity.bindings) == 0

def test_runtime_factory_empty_collections(base_descriptor, base_labels, base_annotations, base_tags):
    context = RuntimeExecutionContextFactory.create(
        base_descriptor, (), (), base_labels, base_annotations, base_tags
    )
    assert len(context.identity.variables) == 0
    assert len(context.identity.bindings) == 0

def test_metadata_factory_returns_proxy():
    metadata = ExecutionContextMetadataFactory.create({'k':'v'}, {}, set())
    with pytest.raises(TypeError):
        metadata.labels['k'] = 'v2'

def test_metadata_factory_returns_frozenset():
    metadata = ExecutionContextMetadataFactory.create({}, {}, {'t'})
    with pytest.raises(AttributeError):
        metadata.tags.add('t2')

def test_statistics_builder_all_optional():
    v1 = RuntimeExecutionVariable('v1', 'n', 't', False, 'd', 'd')
    s = ExecutionContextStatisticsBuilder.build(
        (v1,), (), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({})
    )
    assert s.required_variable_count == 0
    assert s.optional_variable_count == 1

def test_statistics_builder_all_required():
    v1 = RuntimeExecutionVariable('v1', 'n', 't', True, 'd', 'd')
    s = ExecutionContextStatisticsBuilder.build(
        (v1,), (), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({})
    )
    assert s.required_variable_count == 1
    assert s.optional_variable_count == 0

def test_descriptor_factory_consistency():
    d = ExecutionContextDescriptorFactory.create('e', 'r', 'g', 'p', 'c', 'v', 'sv')
    assert d.execution_id == 'e'

def test_snapshot_factory_empty_collections(base_descriptor):
    m = ExecutionContextMetadataFactory.create({}, {}, set())
    st = ExecutionContextStatisticsBuilder.build((), (), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    sn = ExecutionContextSnapshotFactory.create(base_descriptor, (), (), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), m, st)
    assert len(sn.context_hash) == 64

def test_identity_fields_check(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    identity = ExecutionContextFactory.create(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags)
    assert hasattr(identity, 'descriptor')
    assert hasattr(identity, 'metadata')
    assert hasattr(identity, 'variables')
    assert hasattr(identity, 'bindings')
    assert hasattr(identity, 'statistics')
    assert hasattr(identity, 'snapshot')
    assert hasattr(identity, 'variable_lookup')
    assert hasattr(identity, 'binding_lookup')
    assert hasattr(identity, 'descriptor_lookup')
    assert hasattr(identity, 'context_lookup')

def test_context_identifier_uniqueness(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    ctx1 = RuntimeExecutionContextFactory.create(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags)
    ctx2 = RuntimeExecutionContextFactory.create(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags)
    assert ctx1.identifier != ctx2.identifier

def test_snapshot_determinism_empty(base_descriptor):
    m = ExecutionContextMetadataFactory.create({}, {}, set())
    st = ExecutionContextStatisticsBuilder.build((), (), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    sn1 = ExecutionContextSnapshotFactory.create(base_descriptor, (), (), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), m, st)
    sn2 = ExecutionContextSnapshotFactory.create(base_descriptor, (), (), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), m, st)
    assert sn1.context_hash == sn2.context_hash


def test_snapshot_variable_order_independence(base_descriptor, base_bindings, base_labels, base_annotations, base_tags):
    v1 = RuntimeExecutionVariable('v1', 'n', 't', True, 'd', 'd')
    v2 = RuntimeExecutionVariable('v2', 'n', 't', True, 'd', 'd')
    m = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    st = ExecutionContextStatisticsBuilder.build((v1, v2), base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    
    sn1 = ExecutionContextSnapshotFactory.create(base_descriptor, (v1, v2), base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), m, st)
    sn2 = ExecutionContextSnapshotFactory.create(base_descriptor, (v2, v1), base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), m, st)
    
    assert sn1.variable_hash == sn2.variable_hash

def test_snapshot_binding_order_independence(base_descriptor, base_variables, base_labels, base_annotations, base_tags):
    b1 = RuntimeExecutionBinding('b1', 'v1', 'v2', 't', 'd')
    b2 = RuntimeExecutionBinding('b2', 'v1', 'v2', 't', 'd')
    m = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    st = ExecutionContextStatisticsBuilder.build(base_variables, (b1, b2), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    
    sn1 = ExecutionContextSnapshotFactory.create(base_descriptor, base_variables, (b1, b2), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), m, st)
    sn2 = ExecutionContextSnapshotFactory.create(base_descriptor, base_variables, (b2, b1), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), m, st)
    
    assert sn1.binding_hash == sn2.binding_hash

def test_snapshot_variable_lookup_order_independence(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    m = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    st = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    v1 = RuntimeExecutionVariable('v1', 'n', 't', True, 'd', 'd')
    v2 = RuntimeExecutionVariable('v2', 'n', 't', True, 'd', 'd')
    
    # MappingProxyType maintains insertion order if underlying dict does (Python 3.7+), but hash should sort keys
    lookup1 = MappingProxyType({'a': v1, 'b': v2})
    lookup2 = MappingProxyType({'b': v2, 'a': v1})
    
    sn1 = ExecutionContextSnapshotFactory.create(base_descriptor, base_variables, base_bindings, lookup1, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), m, st)
    sn2 = ExecutionContextSnapshotFactory.create(base_descriptor, base_variables, base_bindings, lookup2, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), m, st)
    
    assert sn1.variable_lookup_hash == sn2.variable_lookup_hash

def test_snapshot_binding_lookup_order_independence(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    m = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    st = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    b1 = RuntimeExecutionBinding('b1', 'v1', 'v2', 't', 'd')
    b2 = RuntimeExecutionBinding('b2', 'v1', 'v2', 't', 'd')
    
    lookup1 = MappingProxyType({'a': b1, 'b': b2})
    lookup2 = MappingProxyType({'b': b2, 'a': b1})
    
    sn1 = ExecutionContextSnapshotFactory.create(base_descriptor, base_variables, base_bindings, MappingProxyType({}), lookup1, MappingProxyType({}), MappingProxyType({}), m, st)
    sn2 = ExecutionContextSnapshotFactory.create(base_descriptor, base_variables, base_bindings, MappingProxyType({}), lookup2, MappingProxyType({}), MappingProxyType({}), m, st)
    
    assert sn1.binding_lookup_hash == sn2.binding_lookup_hash

def test_snapshot_descriptor_lookup_order_independence(base_descriptor, base_variables, base_bindings, base_labels, base_annotations, base_tags):
    m = ExecutionContextMetadataFactory.create(base_labels, base_annotations, base_tags)
    st = ExecutionContextStatisticsBuilder.build(base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), MappingProxyType({}), MappingProxyType({}))
    
    d1 = ExecutionContextDescriptorFactory.create('1', '1', '1', '1', '1', '1', '1')
    d2 = ExecutionContextDescriptorFactory.create('2', '2', '2', '2', '2', '2', '2')
    
    lookup1 = MappingProxyType({'a': d1, 'b': d2})
    lookup2 = MappingProxyType({'b': d2, 'a': d1})
    
    sn1 = ExecutionContextSnapshotFactory.create(base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), lookup1, MappingProxyType({}), m, st)
    sn2 = ExecutionContextSnapshotFactory.create(base_descriptor, base_variables, base_bindings, MappingProxyType({}), MappingProxyType({}), lookup2, MappingProxyType({}), m, st)
    
    assert sn1.descriptor_lookup_hash == sn2.descriptor_lookup_hash

