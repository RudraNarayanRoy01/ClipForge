import pytest
import hashlib
from types import MappingProxyType

from src.runtime.execution.runtime_execution_state import RuntimeExecutionState
from src.runtime.execution.runtime_execution_state_identity import RuntimeExecutionStateIdentity
from src.runtime.execution.runtime_execution_state_descriptor import RuntimeExecutionStateDescriptor
from src.runtime.execution.runtime_execution_state_metadata import RuntimeExecutionStateMetadata
from src.runtime.execution.runtime_execution_state_statistics import RuntimeExecutionStateStatistics
from src.runtime.execution.runtime_execution_state_snapshot import RuntimeExecutionStateSnapshot
from src.runtime.execution.runtime_execution_state_validator import RuntimeExecutionStateValidator
from src.runtime.execution.runtime_execution_exceptions import ExecutionValidationException

from src.runtime.execution.execution_state_factory import ExecutionStateFactory
from src.runtime.execution.execution_state_descriptor_factory import ExecutionStateDescriptorFactory
from src.runtime.execution.execution_state_metadata_factory import ExecutionStateMetadataFactory
from src.runtime.execution.execution_state_statistics_builder import ExecutionStateStatisticsBuilder
from src.runtime.execution.execution_state_snapshot_factory import ExecutionStateSnapshotFactory
from src.runtime.execution.runtime_execution_state_factory import RuntimeExecutionStateFactory

from src.runtime.execution.runtime_execution_session import RuntimeExecutionSession

class DummySession(RuntimeExecutionSession):
    pass

@pytest.fixture
def mock_session():
    return DummySession(identifier="sess-123", identity=None)

@pytest.fixture
def valid_descriptor():
    return ExecutionStateDescriptorFactory.create(
        execution_id="exec-123",
        runtime_id="rt-123",
        graph_id="graph-123",
        plan_id="plan-123",
        context_id="ctx-123",
        composition_id="comp-123",
        builder_id="build-123",
        lifecycle_id="life-123",
        scheduler_id="sched-123",
        engine_id="eng-123",
        session_id="sess-123",
        state_id="state-123",
        version="1.0.0",
        schema_version="1.0.0"
    )

@pytest.fixture
def valid_metadata():
    return ExecutionStateMetadataFactory.create(
        labels={"env": "prod"},
        annotations={"author": "ai"},
        tags={"tag1", "tag2"}
    )

@pytest.fixture
def valid_statistics(mock_session):
    return ExecutionStateStatisticsBuilder.build(
        runtime_execution_session=mock_session,
        session_lookup=MappingProxyType({"sess-123": mock_session}),
        descriptor_lookup=MappingProxyType({"state-123": {}}),
        state_lookup=MappingProxyType({"state-123": {}})
    )

@pytest.fixture
def valid_snapshot(valid_descriptor, valid_metadata, valid_statistics, mock_session):
    return ExecutionStateSnapshotFactory.create(
        descriptor=valid_descriptor,
        metadata=valid_metadata,
        statistics=valid_statistics,
        runtime_execution_session=mock_session,
        session_lookup=MappingProxyType({"sess-123": mock_session}),
        descriptor_lookup=MappingProxyType({"state-123": {}}),
        state_lookup=MappingProxyType({"state-123": {}})
    )

@pytest.fixture
def valid_state(valid_descriptor, valid_metadata, valid_statistics, valid_snapshot, mock_session):
    return ExecutionStateFactory.create(
        identifier="state-123",
        descriptor=valid_descriptor,
        metadata=valid_metadata,
        statistics=valid_statistics,
        snapshot=valid_snapshot,
        runtime_execution_session=mock_session,
        session_lookup=MappingProxyType({"sess-123": mock_session}),
        descriptor_lookup=MappingProxyType({"state-123": {}}),
        state_lookup=MappingProxyType({"state-123": {}})
    )

# Ownership Tests
def test_wrapper_ownership(valid_state):
    assert valid_state.identifier == "state-123"
    assert isinstance(valid_state.identity, RuntimeExecutionStateIdentity)
    
    # Negative Ownership
    assert not hasattr(valid_state, "status")
    assert not hasattr(valid_state, "progress")
    assert not hasattr(valid_state, "current_step")
    assert not hasattr(valid_state, "active_task")

def test_identity_ownership(valid_state):
    identity = valid_state.identity
    assert isinstance(identity.descriptor, RuntimeExecutionStateDescriptor)
    assert isinstance(identity.metadata, RuntimeExecutionStateMetadata)
    assert isinstance(identity.statistics, RuntimeExecutionStateStatistics)
    assert isinstance(identity.snapshot, RuntimeExecutionStateSnapshot)
    assert isinstance(identity.runtime_execution_session, RuntimeExecutionSession)
    assert isinstance(identity.session_lookup, MappingProxyType)
    assert isinstance(identity.descriptor_lookup, MappingProxyType)
    assert isinstance(identity.state_lookup, MappingProxyType)
    
    assert not hasattr(identity, "status")
    assert not hasattr(identity, "execution_state")
    assert not hasattr(identity, "progress")

def test_descriptor_ownership(valid_descriptor):
    assert valid_descriptor.execution_id == "exec-123"
    assert valid_descriptor.runtime_id == "rt-123"
    assert valid_descriptor.graph_id == "graph-123"
    assert valid_descriptor.plan_id == "plan-123"
    assert valid_descriptor.context_id == "ctx-123"
    assert valid_descriptor.composition_id == "comp-123"
    assert valid_descriptor.builder_id == "build-123"
    assert valid_descriptor.lifecycle_id == "life-123"
    assert valid_descriptor.scheduler_id == "sched-123"
    assert valid_descriptor.engine_id == "eng-123"
    assert valid_descriptor.session_id == "sess-123"
    assert valid_descriptor.state_id == "state-123"
    assert valid_descriptor.version == "1.0.0"
    assert valid_descriptor.schema_version == "1.0.0"
    
    assert not hasattr(valid_descriptor, "status")
    assert not hasattr(valid_descriptor, "progress")
    assert not hasattr(valid_descriptor, "current_step")
    assert not hasattr(valid_descriptor, "active_task")

def test_metadata_ownership(valid_metadata):
    assert isinstance(valid_metadata.labels, MappingProxyType)
    assert isinstance(valid_metadata.annotations, MappingProxyType)
    assert isinstance(valid_metadata.tags, frozenset)
    assert valid_metadata.labels["env"] == "prod"
    
    assert not hasattr(valid_metadata, "status")
    assert not hasattr(valid_metadata, "progress")

def test_statistics_ownership(valid_statistics):
    assert valid_statistics.session_count == 1
    assert valid_statistics.session_lookup_count == 1
    assert valid_statistics.descriptor_lookup_count == 1
    assert valid_statistics.state_lookup_count == 1
    
    assert not hasattr(valid_statistics, "metrics")
    assert not hasattr(valid_statistics, "duration")

def test_snapshot_ownership(valid_snapshot):
    assert isinstance(valid_snapshot.descriptor_hash, str)
    assert isinstance(valid_snapshot.session_hash, str)
    assert isinstance(valid_snapshot.session_lookup_hash, str)
    assert isinstance(valid_snapshot.descriptor_lookup_hash, str)
    assert isinstance(valid_snapshot.state_lookup_hash, str)
    assert isinstance(valid_snapshot.metadata_hash, str)
    assert isinstance(valid_snapshot.statistics_hash, str)
    assert isinstance(valid_snapshot.state_hash, str)

def test_lookup_ownership(valid_state):
    identity = valid_state.identity
    assert "sess-123" in identity.session_lookup
    assert "state-123" in identity.descriptor_lookup
    assert "state-123" in identity.state_lookup

# Hashing and Determinism Tests
def test_snapshot_determinism(valid_descriptor, valid_metadata, valid_statistics, mock_session):
    s1 = ExecutionStateSnapshotFactory.create(
        valid_descriptor, valid_metadata, valid_statistics, mock_session,
        MappingProxyType({"sess-123": mock_session}), MappingProxyType({"state-123": {}}), MappingProxyType({"state-123": {}})
    )
    s2 = ExecutionStateSnapshotFactory.create(
        valid_descriptor, valid_metadata, valid_statistics, mock_session,
        MappingProxyType({"sess-123": mock_session}), MappingProxyType({"state-123": {}}), MappingProxyType({"state-123": {}})
    )
    assert s1.state_hash == s2.state_hash

def test_insertion_order_independence(valid_descriptor, valid_metadata, valid_statistics, mock_session):
    s1 = ExecutionStateSnapshotFactory.create(
        valid_descriptor, valid_metadata, valid_statistics, mock_session,
        MappingProxyType({"a": 1, "b": 2}), MappingProxyType({"a": 1, "b": 2}), MappingProxyType({"a": 1, "b": 2})
    )
    s2 = ExecutionStateSnapshotFactory.create(
        valid_descriptor, valid_metadata, valid_statistics, mock_session,
        MappingProxyType({"b": 2, "a": 1}), MappingProxyType({"b": 2, "a": 1}), MappingProxyType({"b": 2, "a": 1})
    )
    assert s1.state_hash == s2.state_hash

# Immutability Tests
def test_mapping_proxy_type_enforcement(valid_metadata):
    with pytest.raises(TypeError):
        valid_metadata.labels["new"] = "value"

def test_frozenset_enforcement(valid_metadata):
    with pytest.raises(AttributeError):
        valid_metadata.tags.add("new")

def test_frozen_dataclass_state(valid_state):
    with pytest.raises(Exception):
        valid_state.identifier = "new"

def test_frozen_dataclass_identity(valid_state):
    with pytest.raises(Exception):
        valid_state.identity.descriptor = None

def test_frozen_dataclass_descriptor(valid_descriptor):
    with pytest.raises(Exception):
        valid_descriptor.execution_id = "new"

def test_frozen_dataclass_metadata(valid_metadata):
    with pytest.raises(Exception):
        valid_metadata.labels = None

def test_frozen_dataclass_statistics(valid_statistics):
    with pytest.raises(Exception):
        valid_statistics.session_count = 0

def test_frozen_dataclass_snapshot(valid_snapshot):
    with pytest.raises(Exception):
        valid_snapshot.descriptor_hash = "new"

# Validation Tests
def test_validator_success(valid_state):
    RuntimeExecutionStateValidator.validate(valid_state)

def test_validator_missing_state():
    with pytest.raises(ExecutionValidationException, match="State is missing"):
        RuntimeExecutionStateValidator.validate(None)
        
def test_validator_missing_identity(valid_state):
    invalid = RuntimeExecutionState(identifier="state-123", identity=None)
    with pytest.raises(ExecutionValidationException, match="Identity is missing"):
        RuntimeExecutionStateValidator.validate(invalid)

def test_duplicate_identifier_detection(valid_state):
    invalid_state = RuntimeExecutionState(
        identifier="different-id",
        identity=valid_state.identity
    )
    with pytest.raises(ExecutionValidationException, match="Duplicate identifiers"):
        RuntimeExecutionStateValidator.validate(invalid_state)

def test_missing_session_detection(valid_descriptor, valid_metadata, valid_statistics, valid_snapshot):
    identity = RuntimeExecutionStateIdentity(
        descriptor=valid_descriptor,
        metadata=valid_metadata,
        statistics=valid_statistics,
        snapshot=valid_snapshot,
        runtime_execution_session=None,
        session_lookup=MappingProxyType({"sess-123": {}}),
        descriptor_lookup=MappingProxyType({"state-123": {}}),
        state_lookup=MappingProxyType({"state-123": {}})
    )
    invalid = RuntimeExecutionState(identifier="state-123", identity=identity)
    with pytest.raises(ExecutionValidationException, match="Missing Session"):
        RuntimeExecutionStateValidator.validate(invalid)

def test_validator_missing_session_lookup(valid_state):
    invalid_identity = RuntimeExecutionStateIdentity(
        descriptor=valid_state.identity.descriptor,
        metadata=valid_state.identity.metadata,
        statistics=valid_state.identity.statistics,
        snapshot=valid_state.identity.snapshot,
        runtime_execution_session=valid_state.identity.runtime_execution_session,
        session_lookup=MappingProxyType({}), # Missing
        descriptor_lookup=valid_state.identity.descriptor_lookup,
        state_lookup=valid_state.identity.state_lookup
    )
    invalid = RuntimeExecutionState(identifier="state-123", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException, match="Session not found in session_lookup"):
        RuntimeExecutionStateValidator.validate(invalid)

def test_validator_missing_descriptor_lookup(valid_state):
    invalid_identity = RuntimeExecutionStateIdentity(
        descriptor=valid_state.identity.descriptor,
        metadata=valid_state.identity.metadata,
        statistics=valid_state.identity.statistics,
        snapshot=valid_state.identity.snapshot,
        runtime_execution_session=valid_state.identity.runtime_execution_session,
        session_lookup=valid_state.identity.session_lookup,
        descriptor_lookup=MappingProxyType({}), # Missing
        state_lookup=valid_state.identity.state_lookup
    )
    invalid = RuntimeExecutionState(identifier="state-123", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException, match="Descriptor not found in descriptor_lookup"):
        RuntimeExecutionStateValidator.validate(invalid)

def test_validator_missing_snapshot_hash(valid_state):
    invalid_snapshot = RuntimeExecutionStateSnapshot(
        descriptor_hash="x", session_hash="x", session_lookup_hash="x",
        descriptor_lookup_hash="x", state_lookup_hash="x",
        metadata_hash="x", statistics_hash="x", state_hash="" # Missing
    )
    invalid_identity = RuntimeExecutionStateIdentity(
        descriptor=valid_state.identity.descriptor,
        metadata=valid_state.identity.metadata,
        statistics=valid_state.identity.statistics,
        snapshot=invalid_snapshot,
        runtime_execution_session=valid_state.identity.runtime_execution_session,
        session_lookup=valid_state.identity.session_lookup,
        descriptor_lookup=valid_state.identity.descriptor_lookup,
        state_lookup=valid_state.identity.state_lookup
    )
    invalid = RuntimeExecutionState(identifier="state-123", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException, match="Snapshot consistency error"):
        RuntimeExecutionStateValidator.validate(invalid)

# Factory Isolation Tests
def test_factory_facade_exports():
    assert hasattr(RuntimeExecutionStateFactory, 'create_state')
    assert hasattr(RuntimeExecutionStateFactory, 'create_descriptor')
    assert hasattr(RuntimeExecutionStateFactory, 'create_metadata')
    assert hasattr(RuntimeExecutionStateFactory, 'build_statistics')
    assert hasattr(RuntimeExecutionStateFactory, 'create_snapshot')

# Zero Behaviour Tests
def test_zero_execution_behaviour():
    assert not hasattr(RuntimeExecutionState, 'transition')
    assert not hasattr(RuntimeExecutionState, 'advance')
    assert not hasattr(RuntimeExecutionState, 'update')
    assert not hasattr(RuntimeExecutionState, 'mutate')
    assert not hasattr(RuntimeExecutionState, 'set_state')
    assert not hasattr(RuntimeExecutionState, 'mark_running')
    assert not hasattr(RuntimeExecutionState, 'mark_complete')
    assert not hasattr(RuntimeExecutionState, 'mark_failed')
    assert not hasattr(RuntimeExecutionState, 'retry')
    assert not hasattr(RuntimeExecutionState, 'recover')

def test_zero_provider_execution():
    assert not hasattr(RuntimeExecutionState, 'providers')
    assert not hasattr(RuntimeExecutionState, 'load_provider')
    assert not hasattr(RuntimeExecutionState, 'execute_provider')

def test_zero_ai_execution():
    assert not hasattr(RuntimeExecutionState, 'models')
    assert not hasattr(RuntimeExecutionState, 'prompts')
    assert not hasattr(RuntimeExecutionState, 'execute_ai')

def test_zero_hardware_execution():
    assert not hasattr(RuntimeExecutionState, 'gpu')
    assert not hasattr(RuntimeExecutionState, 'cpu')
    assert not hasattr(RuntimeExecutionState, 'memory')
    assert not hasattr(RuntimeExecutionState, 'hardware')

# Additional explicit property tests
def test_attr_presence_descriptor_execution_id(valid_descriptor):
    assert hasattr(valid_descriptor, "execution_id")
def test_attr_presence_descriptor_runtime_id(valid_descriptor):
    assert hasattr(valid_descriptor, "runtime_id")
def test_attr_presence_descriptor_graph_id(valid_descriptor):
    assert hasattr(valid_descriptor, "graph_id")
def test_attr_presence_descriptor_plan_id(valid_descriptor):
    assert hasattr(valid_descriptor, "plan_id")
def test_attr_presence_descriptor_context_id(valid_descriptor):
    assert hasattr(valid_descriptor, "context_id")
def test_attr_presence_descriptor_composition_id(valid_descriptor):
    assert hasattr(valid_descriptor, "composition_id")
def test_attr_presence_descriptor_builder_id(valid_descriptor):
    assert hasattr(valid_descriptor, "builder_id")
def test_attr_presence_descriptor_lifecycle_id(valid_descriptor):
    assert hasattr(valid_descriptor, "lifecycle_id")
def test_attr_presence_descriptor_scheduler_id(valid_descriptor):
    assert hasattr(valid_descriptor, "scheduler_id")
def test_attr_presence_descriptor_engine_id(valid_descriptor):
    assert hasattr(valid_descriptor, "engine_id")
def test_attr_presence_descriptor_session_id(valid_descriptor):
    assert hasattr(valid_descriptor, "session_id")
def test_attr_presence_descriptor_state_id(valid_descriptor):
    assert hasattr(valid_descriptor, "state_id")
def test_attr_presence_descriptor_version(valid_descriptor):
    assert hasattr(valid_descriptor, "version")
def test_attr_presence_descriptor_schema_version(valid_descriptor):
    assert hasattr(valid_descriptor, "schema_version")

def test_attr_presence_metadata_labels(valid_metadata):
    assert hasattr(valid_metadata, "labels")
def test_attr_presence_metadata_annotations(valid_metadata):
    assert hasattr(valid_metadata, "annotations")
def test_attr_presence_metadata_tags(valid_metadata):
    assert hasattr(valid_metadata, "tags")

def test_attr_presence_statistics_session_count(valid_statistics):
    assert hasattr(valid_statistics, "session_count")
def test_attr_presence_statistics_session_lookup_count(valid_statistics):
    assert hasattr(valid_statistics, "session_lookup_count")
def test_attr_presence_statistics_descriptor_lookup_count(valid_statistics):
    assert hasattr(valid_statistics, "descriptor_lookup_count")
def test_attr_presence_statistics_state_lookup_count(valid_statistics):
    assert hasattr(valid_statistics, "state_lookup_count")

def test_attr_presence_snapshot_descriptor_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "descriptor_hash")
def test_attr_presence_snapshot_session_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "session_hash")
def test_attr_presence_snapshot_session_lookup_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "session_lookup_hash")
def test_attr_presence_snapshot_descriptor_lookup_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "descriptor_lookup_hash")
def test_attr_presence_snapshot_state_lookup_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "state_lookup_hash")
def test_attr_presence_snapshot_metadata_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "metadata_hash")
def test_attr_presence_snapshot_statistics_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "statistics_hash")
def test_attr_presence_snapshot_state_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "state_hash")

def test_attr_presence_identity_descriptor(valid_state):
    assert hasattr(valid_state.identity, "descriptor")
def test_attr_presence_identity_metadata(valid_state):
    assert hasattr(valid_state.identity, "metadata")
def test_attr_presence_identity_statistics(valid_state):
    assert hasattr(valid_state.identity, "statistics")
def test_attr_presence_identity_snapshot(valid_state):
    assert hasattr(valid_state.identity, "snapshot")
def test_attr_presence_identity_session(valid_state):
    assert hasattr(valid_state.identity, "runtime_execution_session")
def test_attr_presence_identity_session_lookup(valid_state):
    assert hasattr(valid_state.identity, "session_lookup")
def test_attr_presence_identity_descriptor_lookup(valid_state):
    assert hasattr(valid_state.identity, "descriptor_lookup")
def test_attr_presence_identity_state_lookup(valid_state):
    assert hasattr(valid_state.identity, "state_lookup")

def test_attr_presence_state_identifier(valid_state):
    assert hasattr(valid_state, "identifier")
def test_attr_presence_state_identity(valid_state):
    assert hasattr(valid_state, "identity")

def test_zero_execution_state():
    assert not hasattr(RuntimeExecutionState, 'execution_state')
    assert not hasattr(RuntimeExecutionStateIdentity, 'execution_state')
def test_zero_execution_progress():
    assert not hasattr(RuntimeExecutionState, 'progress')
    assert not hasattr(RuntimeExecutionStateIdentity, 'progress')
def test_zero_active_task():
    assert not hasattr(RuntimeExecutionState, 'active_task')
def test_zero_worker_state():
    assert not hasattr(RuntimeExecutionState, 'worker_state')
def test_zero_queue_state():
    assert not hasattr(RuntimeExecutionState, 'queue_state')
def test_zero_scheduling_state():
    assert not hasattr(RuntimeExecutionState, 'scheduling_state')
def test_zero_provider_state():
    assert not hasattr(RuntimeExecutionState, 'provider_state')
def test_zero_model_state():
    assert not hasattr(RuntimeExecutionState, 'model_state')
def test_zero_monitoring_state():
    assert not hasattr(RuntimeExecutionState, 'monitoring_state')
def test_zero_telemetry_state():
    assert not hasattr(RuntimeExecutionState, 'telemetry_state')
def test_zero_recovery_state():
    assert not hasattr(RuntimeExecutionState, 'recovery_state')
def test_zero_transition_state():
    assert not hasattr(RuntimeExecutionState, 'transition_state')
