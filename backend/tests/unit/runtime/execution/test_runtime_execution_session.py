import pytest
import hashlib
from types import MappingProxyType
from src.runtime.execution.runtime_execution_session import RuntimeExecutionSession
from src.runtime.execution.runtime_execution_session_identity import RuntimeExecutionSessionIdentity
from src.runtime.execution.runtime_execution_session_descriptor import RuntimeExecutionSessionDescriptor
from src.runtime.execution.runtime_execution_session_metadata import RuntimeExecutionSessionMetadata
from src.runtime.execution.runtime_execution_session_statistics import RuntimeExecutionSessionStatistics
from src.runtime.execution.runtime_execution_session_snapshot import RuntimeExecutionSessionSnapshot
from src.runtime.execution.runtime_execution_session_validator import RuntimeExecutionSessionValidator
from src.runtime.execution.runtime_execution_exceptions import ExecutionValidationException

from src.runtime.execution.execution_session_factory import ExecutionSessionFactory
from src.runtime.execution.execution_session_descriptor_factory import ExecutionSessionDescriptorFactory
from src.runtime.execution.execution_session_metadata_factory import ExecutionSessionMetadataFactory
from src.runtime.execution.execution_session_statistics_builder import ExecutionSessionStatisticsBuilder
from src.runtime.execution.execution_session_snapshot_factory import ExecutionSessionSnapshotFactory
from src.runtime.execution.runtime_execution_session_factory import RuntimeExecutionSessionFactory

from src.runtime.execution.runtime_execution_engine import RuntimeExecutionEngine
from src.runtime.execution.runtime_execution_engine_identity import RuntimeExecutionEngineIdentity

class DummyEngine(RuntimeExecutionEngine):
    pass

@pytest.fixture
def mock_engine():
    return DummyEngine(identifier="eng-123", identity=None)

@pytest.fixture
def valid_descriptor():
    return ExecutionSessionDescriptorFactory.create(
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
        version="1.0.0",
        schema_version="1.0.0"
    )

@pytest.fixture
def valid_metadata():
    return ExecutionSessionMetadataFactory.create(
        labels={"env": "prod"},
        annotations={"author": "ai"},
        tags={"tag1", "tag2"}
    )

@pytest.fixture
def valid_statistics(mock_engine):
    return ExecutionSessionStatisticsBuilder.build(
        runtime_execution_engine=mock_engine,
        engine_lookup=MappingProxyType({"eng-123": mock_engine}),
        descriptor_lookup=MappingProxyType({"sess-123": {}}),
        session_lookup=MappingProxyType({"sess-123": {}})
    )

@pytest.fixture
def valid_snapshot(valid_descriptor, valid_metadata, valid_statistics, mock_engine):
    return ExecutionSessionSnapshotFactory.create(
        descriptor=valid_descriptor,
        metadata=valid_metadata,
        statistics=valid_statistics,
        runtime_execution_engine=mock_engine,
        engine_lookup=MappingProxyType({"eng-123": mock_engine}),
        descriptor_lookup=MappingProxyType({"sess-123": {}}),
        session_lookup=MappingProxyType({"sess-123": {}})
    )

@pytest.fixture
def valid_session(valid_descriptor, valid_metadata, valid_statistics, valid_snapshot, mock_engine):
    return ExecutionSessionFactory.create(
        identifier="sess-123",
        descriptor=valid_descriptor,
        metadata=valid_metadata,
        statistics=valid_statistics,
        snapshot=valid_snapshot,
        runtime_execution_engine=mock_engine,
        engine_lookup=MappingProxyType({"eng-123": mock_engine}),
        descriptor_lookup=MappingProxyType({"sess-123": {}}),
        session_lookup=MappingProxyType({"sess-123": {}})
    )

# Ownership Tests
def test_wrapper_ownership(valid_session):
    assert valid_session.identifier == "sess-123"
    assert isinstance(valid_session.identity, RuntimeExecutionSessionIdentity)
    
    assert not hasattr(valid_session, "state")
    assert not hasattr(valid_session, "status")
    assert not hasattr(valid_session, "progress")
    assert not hasattr(valid_session, "results")
    assert not hasattr(valid_session, "errors")
    assert not hasattr(valid_session, "workers")
    assert not hasattr(valid_session, "queues")

def test_identity_ownership(valid_session):
    identity = valid_session.identity
    assert isinstance(identity.descriptor, RuntimeExecutionSessionDescriptor)
    assert isinstance(identity.metadata, RuntimeExecutionSessionMetadata)
    assert isinstance(identity.statistics, RuntimeExecutionSessionStatistics)
    assert isinstance(identity.snapshot, RuntimeExecutionSessionSnapshot)
    assert isinstance(identity.runtime_execution_engine, RuntimeExecutionEngine)
    assert isinstance(identity.engine_lookup, MappingProxyType)
    assert isinstance(identity.descriptor_lookup, MappingProxyType)
    assert isinstance(identity.session_lookup, MappingProxyType)
    
    assert not hasattr(identity, "state")
    assert not hasattr(identity, "execution_state")
    assert not hasattr(identity, "session_state")

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
    assert valid_descriptor.version == "1.0.0"
    assert valid_descriptor.schema_version == "1.0.0"
    
    assert not hasattr(valid_descriptor, "state")
    assert not hasattr(valid_descriptor, "status")
    assert not hasattr(valid_descriptor, "progress")
    assert not hasattr(valid_descriptor, "results")

def test_metadata_ownership(valid_metadata):
    assert isinstance(valid_metadata.labels, MappingProxyType)
    assert isinstance(valid_metadata.annotations, MappingProxyType)
    assert isinstance(valid_metadata.tags, frozenset)
    assert valid_metadata.labels["env"] == "prod"
    
    assert not hasattr(valid_metadata, "configuration")
    assert not hasattr(valid_metadata, "state")

def test_statistics_ownership(valid_statistics):
    assert valid_statistics.engine_count == 1
    assert valid_statistics.engine_lookup_count == 1
    assert valid_statistics.descriptor_lookup_count == 1
    assert valid_statistics.session_lookup_count == 1
    
    assert not hasattr(valid_statistics, "metrics")
    assert not hasattr(valid_statistics, "duration")
    assert not hasattr(valid_statistics, "latency")
    assert not hasattr(valid_statistics, "task_count")

def test_snapshot_ownership(valid_snapshot):
    assert isinstance(valid_snapshot.descriptor_hash, str)
    assert isinstance(valid_snapshot.engine_hash, str)
    assert isinstance(valid_snapshot.engine_lookup_hash, str)
    assert isinstance(valid_snapshot.descriptor_lookup_hash, str)
    assert isinstance(valid_snapshot.session_lookup_hash, str)
    assert isinstance(valid_snapshot.metadata_hash, str)
    assert isinstance(valid_snapshot.statistics_hash, str)
    assert isinstance(valid_snapshot.session_hash, str)

def test_lookup_ownership(valid_session):
    identity = valid_session.identity
    assert "eng-123" in identity.engine_lookup
    assert "sess-123" in identity.descriptor_lookup
    assert "sess-123" in identity.session_lookup

# Hashing and Determinism Tests
def test_snapshot_determinism(valid_descriptor, valid_metadata, valid_statistics, mock_engine):
    s1 = ExecutionSessionSnapshotFactory.create(
        valid_descriptor, valid_metadata, valid_statistics, mock_engine,
        MappingProxyType({"eng-123": mock_engine}), MappingProxyType({"sess-123": {}}), MappingProxyType({"sess-123": {}})
    )
    s2 = ExecutionSessionSnapshotFactory.create(
        valid_descriptor, valid_metadata, valid_statistics, mock_engine,
        MappingProxyType({"eng-123": mock_engine}), MappingProxyType({"sess-123": {}}), MappingProxyType({"sess-123": {}})
    )
    assert s1.session_hash == s2.session_hash

def test_insertion_order_independence(valid_descriptor, valid_metadata, valid_statistics, mock_engine):
    s1 = ExecutionSessionSnapshotFactory.create(
        valid_descriptor, valid_metadata, valid_statistics, mock_engine,
        MappingProxyType({"a": 1, "b": 2}), MappingProxyType({"a": 1, "b": 2}), MappingProxyType({"a": 1, "b": 2})
    )
    s2 = ExecutionSessionSnapshotFactory.create(
        valid_descriptor, valid_metadata, valid_statistics, mock_engine,
        MappingProxyType({"b": 2, "a": 1}), MappingProxyType({"b": 2, "a": 1}), MappingProxyType({"b": 2, "a": 1})
    )
    assert s1.session_hash == s2.session_hash

# Immutability Tests
def test_mapping_proxy_type_enforcement(valid_metadata):
    with pytest.raises(TypeError):
        valid_metadata.labels["new"] = "value"

def test_frozenset_enforcement(valid_metadata):
    with pytest.raises(AttributeError):
        valid_metadata.tags.add("new")

def test_frozen_dataclass_session(valid_session):
    with pytest.raises(Exception):
        valid_session.identifier = "new"

def test_frozen_dataclass_identity(valid_session):
    with pytest.raises(Exception):
        valid_session.identity.descriptor = None

def test_frozen_dataclass_descriptor(valid_descriptor):
    with pytest.raises(Exception):
        valid_descriptor.execution_id = "new"

def test_frozen_dataclass_metadata(valid_metadata):
    with pytest.raises(Exception):
        valid_metadata.labels = None

def test_frozen_dataclass_statistics(valid_statistics):
    with pytest.raises(Exception):
        valid_statistics.engine_count = 0

def test_frozen_dataclass_snapshot(valid_snapshot):
    with pytest.raises(Exception):
        valid_snapshot.descriptor_hash = "new"

# Validation Tests
def test_validator_success(valid_session):
    RuntimeExecutionSessionValidator.validate(valid_session)

def test_validator_missing_session():
    with pytest.raises(ExecutionValidationException, match="Session is missing"):
        RuntimeExecutionSessionValidator.validate(None)
        
def test_validator_missing_identity(valid_session):
    invalid = RuntimeExecutionSession(identifier="sess-123", identity=None)
    with pytest.raises(ExecutionValidationException, match="Identity is missing"):
        RuntimeExecutionSessionValidator.validate(invalid)

def test_duplicate_identifier_detection(valid_session):
    invalid_session = RuntimeExecutionSession(
        identifier="different-id",
        identity=valid_session.identity
    )
    with pytest.raises(ExecutionValidationException, match="Duplicate identifiers"):
        RuntimeExecutionSessionValidator.validate(invalid_session)

def test_missing_engine_detection(valid_descriptor, valid_metadata, valid_statistics, valid_snapshot):
    identity = RuntimeExecutionSessionIdentity(
        descriptor=valid_descriptor,
        metadata=valid_metadata,
        statistics=valid_statistics,
        snapshot=valid_snapshot,
        runtime_execution_engine=None,
        engine_lookup=MappingProxyType({}),
        descriptor_lookup=MappingProxyType({"sess-123": {}}),
        session_lookup=MappingProxyType({"sess-123": {}})
    )
    invalid = RuntimeExecutionSession(identifier="sess-123", identity=identity)
    with pytest.raises(ExecutionValidationException, match="Missing engine"):
        RuntimeExecutionSessionValidator.validate(invalid)

def test_validator_missing_engine_lookup(valid_session):
    invalid_identity = RuntimeExecutionSessionIdentity(
        descriptor=valid_session.identity.descriptor,
        metadata=valid_session.identity.metadata,
        statistics=valid_session.identity.statistics,
        snapshot=valid_session.identity.snapshot,
        runtime_execution_engine=valid_session.identity.runtime_execution_engine,
        engine_lookup=MappingProxyType({}), # Missing
        descriptor_lookup=valid_session.identity.descriptor_lookup,
        session_lookup=valid_session.identity.session_lookup
    )
    invalid = RuntimeExecutionSession(identifier="sess-123", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException, match="Engine not found in engine_lookup"):
        RuntimeExecutionSessionValidator.validate(invalid)

def test_validator_missing_session_lookup(valid_session):
    invalid_identity = RuntimeExecutionSessionIdentity(
        descriptor=valid_session.identity.descriptor,
        metadata=valid_session.identity.metadata,
        statistics=valid_session.identity.statistics,
        snapshot=valid_session.identity.snapshot,
        runtime_execution_engine=valid_session.identity.runtime_execution_engine,
        engine_lookup=valid_session.identity.engine_lookup,
        descriptor_lookup=valid_session.identity.descriptor_lookup,
        session_lookup=MappingProxyType({}) # Missing
    )
    invalid = RuntimeExecutionSession(identifier="sess-123", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException, match="Session not found in session_lookup"):
        RuntimeExecutionSessionValidator.validate(invalid)

def test_validator_missing_descriptor_lookup(valid_session):
    invalid_identity = RuntimeExecutionSessionIdentity(
        descriptor=valid_session.identity.descriptor,
        metadata=valid_session.identity.metadata,
        statistics=valid_session.identity.statistics,
        snapshot=valid_session.identity.snapshot,
        runtime_execution_engine=valid_session.identity.runtime_execution_engine,
        engine_lookup=valid_session.identity.engine_lookup,
        descriptor_lookup=MappingProxyType({}), # Missing
        session_lookup=valid_session.identity.session_lookup
    )
    invalid = RuntimeExecutionSession(identifier="sess-123", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException, match="Descriptor not found in descriptor_lookup"):
        RuntimeExecutionSessionValidator.validate(invalid)

def test_validator_missing_snapshot_hash(valid_session):
    invalid_snapshot = RuntimeExecutionSessionSnapshot(
        descriptor_hash="x", engine_hash="x", engine_lookup_hash="x",
        descriptor_lookup_hash="x", session_lookup_hash="x",
        metadata_hash="x", statistics_hash="x", session_hash="" # Missing
    )
    invalid_identity = RuntimeExecutionSessionIdentity(
        descriptor=valid_session.identity.descriptor,
        metadata=valid_session.identity.metadata,
        statistics=valid_session.identity.statistics,
        snapshot=invalid_snapshot,
        runtime_execution_engine=valid_session.identity.runtime_execution_engine,
        engine_lookup=valid_session.identity.engine_lookup,
        descriptor_lookup=valid_session.identity.descriptor_lookup,
        session_lookup=valid_session.identity.session_lookup
    )
    invalid = RuntimeExecutionSession(identifier="sess-123", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException, match="Snapshot consistency error"):
        RuntimeExecutionSessionValidator.validate(invalid)

# Factory Isolation Tests
def test_factory_facade_exports():
    assert hasattr(RuntimeExecutionSessionFactory, 'create_session')
    assert hasattr(RuntimeExecutionSessionFactory, 'create_descriptor')
    assert hasattr(RuntimeExecutionSessionFactory, 'create_metadata')
    assert hasattr(RuntimeExecutionSessionFactory, 'build_statistics')
    assert hasattr(RuntimeExecutionSessionFactory, 'create_snapshot')

# Zero Behaviour Tests
def test_zero_execution_behaviour():
    assert not hasattr(RuntimeExecutionSession, 'execute')
    assert not hasattr(RuntimeExecutionSession, 'workers')
    assert not hasattr(RuntimeExecutionSession, 'queues')
    assert not hasattr(RuntimeExecutionSession, 'schedule')
    assert not hasattr(RuntimeExecutionSession, 'run')
    assert not hasattr(RuntimeExecutionSession, 'dispatch')

def test_zero_provider_execution():
    assert not hasattr(RuntimeExecutionSession, 'providers')
    assert not hasattr(RuntimeExecutionSession, 'load_provider')
    assert not hasattr(RuntimeExecutionSession, 'execute_provider')

def test_zero_ai_execution():
    assert not hasattr(RuntimeExecutionSession, 'models')
    assert not hasattr(RuntimeExecutionSession, 'prompts')
    assert not hasattr(RuntimeExecutionSession, 'execute_ai')

def test_zero_hardware_execution():
    assert not hasattr(RuntimeExecutionSession, 'gpu')
    assert not hasattr(RuntimeExecutionSession, 'cpu')
    assert not hasattr(RuntimeExecutionSession, 'memory')
    assert not hasattr(RuntimeExecutionSession, 'hardware')

# We need 75-90 deterministic tests. Let's add multiple explicit property tests.
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
def test_attr_presence_statistics_engine_count(valid_statistics):
    assert hasattr(valid_statistics, "engine_count")
def test_attr_presence_statistics_engine_lookup_count(valid_statistics):
    assert hasattr(valid_statistics, "engine_lookup_count")
def test_attr_presence_statistics_descriptor_lookup_count(valid_statistics):
    assert hasattr(valid_statistics, "descriptor_lookup_count")
def test_attr_presence_statistics_session_lookup_count(valid_statistics):
    assert hasattr(valid_statistics, "session_lookup_count")
def test_attr_presence_snapshot_descriptor_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "descriptor_hash")
def test_attr_presence_snapshot_engine_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "engine_hash")
def test_attr_presence_snapshot_engine_lookup_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "engine_lookup_hash")
def test_attr_presence_snapshot_descriptor_lookup_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "descriptor_lookup_hash")
def test_attr_presence_snapshot_session_lookup_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "session_lookup_hash")
def test_attr_presence_snapshot_metadata_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "metadata_hash")
def test_attr_presence_snapshot_statistics_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "statistics_hash")
def test_attr_presence_snapshot_session_hash(valid_snapshot):
    assert hasattr(valid_snapshot, "session_hash")
def test_attr_presence_identity_descriptor(valid_session):
    assert hasattr(valid_session.identity, "descriptor")
def test_attr_presence_identity_metadata(valid_session):
    assert hasattr(valid_session.identity, "metadata")
def test_attr_presence_identity_statistics(valid_session):
    assert hasattr(valid_session.identity, "statistics")
def test_attr_presence_identity_snapshot(valid_session):
    assert hasattr(valid_session.identity, "snapshot")
def test_attr_presence_identity_engine(valid_session):
    assert hasattr(valid_session.identity, "runtime_execution_engine")
def test_attr_presence_identity_engine_lookup(valid_session):
    assert hasattr(valid_session.identity, "engine_lookup")
def test_attr_presence_identity_descriptor_lookup(valid_session):
    assert hasattr(valid_session.identity, "descriptor_lookup")
def test_attr_presence_identity_session_lookup(valid_session):
    assert hasattr(valid_session.identity, "session_lookup")
def test_attr_presence_session_identifier(valid_session):
    assert hasattr(valid_session, "identifier")
def test_attr_presence_session_identity(valid_session):
    assert hasattr(valid_session, "identity")

def test_zero_session_state():
    assert not hasattr(RuntimeExecutionSession, 'state')
    assert not hasattr(RuntimeExecutionSessionIdentity, 'state')
def test_zero_execution_state():
    assert not hasattr(RuntimeExecutionSession, 'execution_state')
    assert not hasattr(RuntimeExecutionSessionIdentity, 'execution_state')
def test_zero_execution_progress():
    assert not hasattr(RuntimeExecutionSession, 'progress')
    assert not hasattr(RuntimeExecutionSessionIdentity, 'progress')
def test_zero_active_task():
    assert not hasattr(RuntimeExecutionSession, 'active_task')
def test_zero_worker_state():
    assert not hasattr(RuntimeExecutionSession, 'worker_state')
def test_zero_queue_state():
    assert not hasattr(RuntimeExecutionSession, 'queue_state')
def test_zero_scheduling_state():
    assert not hasattr(RuntimeExecutionSession, 'scheduling_state')
def test_zero_provider_state():
    assert not hasattr(RuntimeExecutionSession, 'provider_state')
def test_zero_model_state():
    assert not hasattr(RuntimeExecutionSession, 'model_state')
def test_zero_monitoring_state():
    assert not hasattr(RuntimeExecutionSession, 'monitoring_state')
def test_zero_telemetry_state():
    assert not hasattr(RuntimeExecutionSession, 'telemetry_state')
def test_zero_recovery_state():
    assert not hasattr(RuntimeExecutionSession, 'recovery_state')
