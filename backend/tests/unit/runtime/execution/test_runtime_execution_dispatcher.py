import pytest
import hashlib
from types import MappingProxyType

from src.runtime.execution.runtime_execution_dispatcher import RuntimeExecutionDispatcher
from src.runtime.execution.runtime_execution_dispatcher_identity import RuntimeExecutionDispatcherIdentity
from src.runtime.execution.runtime_execution_dispatcher_descriptor import RuntimeExecutionDispatcherDescriptor
from src.runtime.execution.runtime_execution_dispatcher_metadata import RuntimeExecutionDispatcherMetadata
from src.runtime.execution.runtime_execution_dispatcher_statistics import RuntimeExecutionDispatcherStatistics
from src.runtime.execution.runtime_execution_dispatcher_snapshot import RuntimeExecutionDispatcherSnapshot
from src.runtime.execution.runtime_execution_dispatcher_validator import RuntimeExecutionDispatcherValidator
from src.runtime.execution.runtime_execution_exceptions import ExecutionValidationException

from src.runtime.execution.execution_dispatcher_factory import ExecutionDispatcherFactory
from src.runtime.execution.execution_dispatcher_descriptor_factory import ExecutionDispatcherDescriptorFactory
from src.runtime.execution.execution_dispatcher_metadata_factory import ExecutionDispatcherMetadataFactory
from src.runtime.execution.execution_dispatcher_statistics_builder import ExecutionDispatcherStatisticsBuilder
from src.runtime.execution.execution_dispatcher_snapshot_factory import ExecutionDispatcherSnapshotFactory
from src.runtime.execution.runtime_execution_dispatcher_factory import RuntimeExecutionDispatcherFactory

from src.runtime.execution.runtime_execution_state import RuntimeExecutionState

class DummyState(RuntimeExecutionState):
    pass

@pytest.fixture
def mock_state():
    return DummyState(identifier="state-123", identity=None)

@pytest.fixture
def valid_descriptor():
    return ExecutionDispatcherDescriptorFactory.create(
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
        dispatcher_id="dispatch-123",
        version="1.0.0",
        schema_version="1.0.0"
    )

@pytest.fixture
def valid_metadata():
    return ExecutionDispatcherMetadataFactory.create(
        labels={"env": "prod"},
        annotations={"author": "ai"},
        tags={"tag1", "tag2"}
    )

@pytest.fixture
def valid_statistics(mock_state):
    return ExecutionDispatcherStatisticsBuilder.build(
        runtime_execution_state=mock_state,
        state_lookup=MappingProxyType({"state-123": mock_state}),
        descriptor_lookup=MappingProxyType({"dispatch-123": {}}),
        dispatcher_lookup=MappingProxyType({"dispatch-123": {}})
    )

@pytest.fixture
def valid_snapshot(valid_descriptor, valid_metadata, valid_statistics, mock_state):
    return ExecutionDispatcherSnapshotFactory.create(
        descriptor=valid_descriptor,
        metadata=valid_metadata,
        statistics=valid_statistics,
        runtime_execution_state=mock_state,
        state_lookup=MappingProxyType({"state-123": mock_state}),
        descriptor_lookup=MappingProxyType({"dispatch-123": {}}),
        dispatcher_lookup=MappingProxyType({"dispatch-123": {}})
    )

@pytest.fixture
def valid_dispatcher(valid_descriptor, valid_metadata, valid_statistics, valid_snapshot, mock_state):
    return ExecutionDispatcherFactory.create(
        identifier="dispatch-123",
        descriptor=valid_descriptor,
        metadata=valid_metadata,
        statistics=valid_statistics,
        snapshot=valid_snapshot,
        runtime_execution_state=mock_state,
        state_lookup=MappingProxyType({"state-123": mock_state}),
        descriptor_lookup=MappingProxyType({"dispatch-123": {}}),
        dispatcher_lookup=MappingProxyType({"dispatch-123": {}})
    )

# Ownership Tests
def test_wrapper_ownership(valid_dispatcher):
    assert valid_dispatcher.identifier == "dispatch-123"
    assert isinstance(valid_dispatcher.identity, RuntimeExecutionDispatcherIdentity)
    
    # Negative Ownership
    assert not hasattr(valid_dispatcher, "status")
    assert not hasattr(valid_dispatcher, "dispatch_status")
    assert not hasattr(valid_dispatcher, "worker")
    assert not hasattr(valid_dispatcher, "queue")

def test_identity_ownership(valid_dispatcher):
    identity = valid_dispatcher.identity
    assert isinstance(identity.descriptor, RuntimeExecutionDispatcherDescriptor)
    assert isinstance(identity.metadata, RuntimeExecutionDispatcherMetadata)
    assert isinstance(identity.statistics, RuntimeExecutionDispatcherStatistics)
    assert isinstance(identity.snapshot, RuntimeExecutionDispatcherSnapshot)
    assert isinstance(identity.runtime_execution_state, RuntimeExecutionState)
    assert isinstance(identity.state_lookup, MappingProxyType)
    assert isinstance(identity.descriptor_lookup, MappingProxyType)
    assert isinstance(identity.dispatcher_lookup, MappingProxyType)
    
    assert not hasattr(identity, "status")
    assert not hasattr(identity, "dispatch_state")
    assert not hasattr(identity, "worker_state")

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
    assert valid_descriptor.dispatcher_id == "dispatch-123"
    assert valid_descriptor.version == "1.0.0"
    assert valid_descriptor.schema_version == "1.0.0"
    
    assert not hasattr(valid_descriptor, "status")
    assert not hasattr(valid_descriptor, "worker_id")
    assert not hasattr(valid_descriptor, "queue_id")
    assert not hasattr(valid_descriptor, "provider_id")

def test_metadata_ownership(valid_metadata):
    assert isinstance(valid_metadata.labels, MappingProxyType)
    assert isinstance(valid_metadata.annotations, MappingProxyType)
    assert isinstance(valid_metadata.tags, frozenset)
    assert valid_metadata.labels["env"] == "prod"
    
    assert not hasattr(valid_metadata, "target_worker")
    assert not hasattr(valid_metadata, "route")

def test_statistics_ownership(valid_statistics):
    assert valid_statistics.state_count == 1
    assert valid_statistics.state_lookup_count == 1
    assert valid_statistics.descriptor_lookup_count == 1
    assert valid_statistics.dispatcher_lookup_count == 1
    
    assert not hasattr(valid_statistics, "dispatch_count")
    assert not hasattr(valid_statistics, "queue_wait_time")
    assert not hasattr(valid_statistics, "worker_utilization")

def test_snapshot_ownership(valid_snapshot):
    assert isinstance(valid_snapshot.descriptor_hash, str)
    assert isinstance(valid_snapshot.state_hash, str)
    assert isinstance(valid_snapshot.state_lookup_hash, str)
    assert isinstance(valid_snapshot.descriptor_lookup_hash, str)
    assert isinstance(valid_snapshot.dispatcher_lookup_hash, str)
    assert isinstance(valid_snapshot.metadata_hash, str)
    assert isinstance(valid_snapshot.statistics_hash, str)
    assert isinstance(valid_snapshot.dispatcher_hash, str)

def test_lookup_ownership(valid_dispatcher):
    identity = valid_dispatcher.identity
    assert "state-123" in identity.state_lookup
    assert "dispatch-123" in identity.descriptor_lookup
    assert "dispatch-123" in identity.dispatcher_lookup

# Hashing and Determinism Tests
def test_snapshot_determinism(valid_descriptor, valid_metadata, valid_statistics, mock_state):
    s1 = ExecutionDispatcherSnapshotFactory.create(
        valid_descriptor, valid_metadata, valid_statistics, mock_state,
        MappingProxyType({"state-123": mock_state}), MappingProxyType({"dispatch-123": {}}), MappingProxyType({"dispatch-123": {}})
    )
    s2 = ExecutionDispatcherSnapshotFactory.create(
        valid_descriptor, valid_metadata, valid_statistics, mock_state,
        MappingProxyType({"state-123": mock_state}), MappingProxyType({"dispatch-123": {}}), MappingProxyType({"dispatch-123": {}})
    )
    assert s1.dispatcher_hash == s2.dispatcher_hash

def test_insertion_order_independence(valid_descriptor, valid_metadata, valid_statistics, mock_state):
    s1 = ExecutionDispatcherSnapshotFactory.create(
        valid_descriptor, valid_metadata, valid_statistics, mock_state,
        MappingProxyType({"a": 1, "b": 2}), MappingProxyType({"a": 1, "b": 2}), MappingProxyType({"a": 1, "b": 2})
    )
    s2 = ExecutionDispatcherSnapshotFactory.create(
        valid_descriptor, valid_metadata, valid_statistics, mock_state,
        MappingProxyType({"b": 2, "a": 1}), MappingProxyType({"b": 2, "a": 1}), MappingProxyType({"b": 2, "a": 1})
    )
    assert s1.dispatcher_hash == s2.dispatcher_hash

# Immutability Tests
def test_mapping_proxy_type_enforcement(valid_metadata):
    with pytest.raises(TypeError):
        valid_metadata.labels["new"] = "value"

def test_frozenset_enforcement(valid_metadata):
    with pytest.raises(AttributeError):
        valid_metadata.tags.add("new")

def test_frozen_dataclass_dispatcher(valid_dispatcher):
    with pytest.raises(Exception):
        valid_dispatcher.identifier = "new"

def test_frozen_dataclass_identity(valid_dispatcher):
    with pytest.raises(Exception):
        valid_dispatcher.identity.descriptor = None

def test_frozen_dataclass_descriptor(valid_descriptor):
    with pytest.raises(Exception):
        valid_descriptor.execution_id = "new"

def test_frozen_dataclass_metadata(valid_metadata):
    with pytest.raises(Exception):
        valid_metadata.labels = None

def test_frozen_dataclass_statistics(valid_statistics):
    with pytest.raises(Exception):
        valid_statistics.state_count = 0

def test_frozen_dataclass_snapshot(valid_snapshot):
    with pytest.raises(Exception):
        valid_snapshot.descriptor_hash = "new"

# Validation Tests
def test_validator_success(valid_dispatcher):
    RuntimeExecutionDispatcherValidator.validate(valid_dispatcher)

def test_validator_missing_dispatcher():
    with pytest.raises(ExecutionValidationException, match="Dispatcher is missing"):
        RuntimeExecutionDispatcherValidator.validate(None)
        
def test_validator_missing_identity(valid_dispatcher):
    invalid = RuntimeExecutionDispatcher(identifier="dispatch-123", identity=None)
    with pytest.raises(ExecutionValidationException, match="Identity is missing"):
        RuntimeExecutionDispatcherValidator.validate(invalid)

def test_duplicate_identifier_detection(valid_dispatcher):
    invalid_dispatcher = RuntimeExecutionDispatcher(
        identifier="different-id",
        identity=valid_dispatcher.identity
    )
    with pytest.raises(ExecutionValidationException, match="Duplicate identifiers"):
        RuntimeExecutionDispatcherValidator.validate(invalid_dispatcher)

def test_missing_state_detection(valid_descriptor, valid_metadata, valid_statistics, valid_snapshot):
    identity = RuntimeExecutionDispatcherIdentity(
        descriptor=valid_descriptor,
        metadata=valid_metadata,
        statistics=valid_statistics,
        snapshot=valid_snapshot,
        runtime_execution_state=None,
        state_lookup=MappingProxyType({"state-123": {}}),
        descriptor_lookup=MappingProxyType({"dispatch-123": {}}),
        dispatcher_lookup=MappingProxyType({"dispatch-123": {}})
    )
    invalid = RuntimeExecutionDispatcher(identifier="dispatch-123", identity=identity)
    with pytest.raises(ExecutionValidationException, match="Missing State"):
        RuntimeExecutionDispatcherValidator.validate(invalid)

def test_validator_missing_state_lookup(valid_dispatcher):
    invalid_identity = RuntimeExecutionDispatcherIdentity(
        descriptor=valid_dispatcher.identity.descriptor,
        metadata=valid_dispatcher.identity.metadata,
        statistics=valid_dispatcher.identity.statistics,
        snapshot=valid_dispatcher.identity.snapshot,
        runtime_execution_state=valid_dispatcher.identity.runtime_execution_state,
        state_lookup=MappingProxyType({}), # Missing
        descriptor_lookup=valid_dispatcher.identity.descriptor_lookup,
        dispatcher_lookup=valid_dispatcher.identity.dispatcher_lookup
    )
    invalid = RuntimeExecutionDispatcher(identifier="dispatch-123", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException, match="State not found in state_lookup"):
        RuntimeExecutionDispatcherValidator.validate(invalid)

def test_validator_missing_descriptor_lookup(valid_dispatcher):
    invalid_identity = RuntimeExecutionDispatcherIdentity(
        descriptor=valid_dispatcher.identity.descriptor,
        metadata=valid_dispatcher.identity.metadata,
        statistics=valid_dispatcher.identity.statistics,
        snapshot=valid_dispatcher.identity.snapshot,
        runtime_execution_state=valid_dispatcher.identity.runtime_execution_state,
        state_lookup=valid_dispatcher.identity.state_lookup,
        descriptor_lookup=MappingProxyType({}), # Missing
        dispatcher_lookup=valid_dispatcher.identity.dispatcher_lookup
    )
    invalid = RuntimeExecutionDispatcher(identifier="dispatch-123", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException, match="Descriptor not found in descriptor_lookup"):
        RuntimeExecutionDispatcherValidator.validate(invalid)

def test_validator_missing_snapshot_hash(valid_dispatcher):
    invalid_snapshot = RuntimeExecutionDispatcherSnapshot(
        descriptor_hash="x", state_hash="x", state_lookup_hash="x",
        descriptor_lookup_hash="x", dispatcher_lookup_hash="x",
        metadata_hash="x", statistics_hash="x", dispatcher_hash="" # Missing
    )
    invalid_identity = RuntimeExecutionDispatcherIdentity(
        descriptor=valid_dispatcher.identity.descriptor,
        metadata=valid_dispatcher.identity.metadata,
        statistics=valid_dispatcher.identity.statistics,
        snapshot=invalid_snapshot,
        runtime_execution_state=valid_dispatcher.identity.runtime_execution_state,
        state_lookup=valid_dispatcher.identity.state_lookup,
        descriptor_lookup=valid_dispatcher.identity.descriptor_lookup,
        dispatcher_lookup=valid_dispatcher.identity.dispatcher_lookup
    )
    invalid = RuntimeExecutionDispatcher(identifier="dispatch-123", identity=invalid_identity)
    with pytest.raises(ExecutionValidationException, match="Snapshot consistency error"):
        RuntimeExecutionDispatcherValidator.validate(invalid)

# Factory Isolation Tests
def test_factory_facade_exports():
    assert hasattr(RuntimeExecutionDispatcherFactory, 'create_dispatcher')
    assert hasattr(RuntimeExecutionDispatcherFactory, 'create_descriptor')
    assert hasattr(RuntimeExecutionDispatcherFactory, 'create_metadata')
    assert hasattr(RuntimeExecutionDispatcherFactory, 'build_statistics')
    assert hasattr(RuntimeExecutionDispatcherFactory, 'create_snapshot')

# Zero Behaviour Tests
def test_zero_dispatch_behaviour():
    assert not hasattr(RuntimeExecutionDispatcher, 'dispatch')
    assert not hasattr(RuntimeExecutionDispatcher, 'execute')
    assert not hasattr(RuntimeExecutionDispatcher, 'route')
    assert not hasattr(RuntimeExecutionDispatcher, 'schedule')
    assert not hasattr(RuntimeExecutionDispatcher, 'submit')
    assert not hasattr(RuntimeExecutionDispatcher, 'enqueue')
    assert not hasattr(RuntimeExecutionDispatcher, 'dequeue')
    assert not hasattr(RuntimeExecutionDispatcher, 'assign')
    assert not hasattr(RuntimeExecutionDispatcher, 'assign_worker')
    assert not hasattr(RuntimeExecutionDispatcher, 'select_worker')
    assert not hasattr(RuntimeExecutionDispatcher, 'select_queue')
    assert not hasattr(RuntimeExecutionDispatcher, 'select_provider')
    assert not hasattr(RuntimeExecutionDispatcher, 'select_model')
    assert not hasattr(RuntimeExecutionDispatcher, 'retry')
    assert not hasattr(RuntimeExecutionDispatcher, 'recover')
    assert not hasattr(RuntimeExecutionDispatcher, 'cancel')
    assert not hasattr(RuntimeExecutionDispatcher, 'update')
    assert not hasattr(RuntimeExecutionDispatcher, 'mutate')
    assert not hasattr(RuntimeExecutionDispatcher, 'transition')
    assert not hasattr(RuntimeExecutionDispatcher, 'advance')

def test_zero_provider_execution():
    assert not hasattr(RuntimeExecutionDispatcher, 'providers')
    assert not hasattr(RuntimeExecutionDispatcher, 'load_provider')
    assert not hasattr(RuntimeExecutionDispatcher, 'execute_provider')

def test_zero_ai_execution():
    assert not hasattr(RuntimeExecutionDispatcher, 'models')
    assert not hasattr(RuntimeExecutionDispatcher, 'prompts')
    assert not hasattr(RuntimeExecutionDispatcher, 'execute_ai')

def test_zero_hardware_execution():
    assert not hasattr(RuntimeExecutionDispatcher, 'gpu')
    assert not hasattr(RuntimeExecutionDispatcher, 'cpu')
    assert not hasattr(RuntimeExecutionDispatcher, 'memory')
    assert not hasattr(RuntimeExecutionDispatcher, 'hardware')

# Additional explicit property tests
def test_attr_presence_descriptor_fields(valid_descriptor):
    assert hasattr(valid_descriptor, "execution_id")
    assert hasattr(valid_descriptor, "runtime_id")
    assert hasattr(valid_descriptor, "graph_id")
    assert hasattr(valid_descriptor, "plan_id")
    assert hasattr(valid_descriptor, "context_id")
    assert hasattr(valid_descriptor, "composition_id")
    assert hasattr(valid_descriptor, "builder_id")
    assert hasattr(valid_descriptor, "lifecycle_id")
    assert hasattr(valid_descriptor, "scheduler_id")
    assert hasattr(valid_descriptor, "engine_id")
    assert hasattr(valid_descriptor, "session_id")
    assert hasattr(valid_descriptor, "state_id")
    assert hasattr(valid_descriptor, "dispatcher_id")
    assert hasattr(valid_descriptor, "version")
    assert hasattr(valid_descriptor, "schema_version")

def test_attr_presence_metadata_fields(valid_metadata):
    assert hasattr(valid_metadata, "labels")
    assert hasattr(valid_metadata, "annotations")
    assert hasattr(valid_metadata, "tags")

def test_attr_presence_statistics_fields(valid_statistics):
    assert hasattr(valid_statistics, "state_count")
    assert hasattr(valid_statistics, "state_lookup_count")
    assert hasattr(valid_statistics, "descriptor_lookup_count")
    assert hasattr(valid_statistics, "dispatcher_lookup_count")

def test_attr_presence_snapshot_fields(valid_snapshot):
    assert hasattr(valid_snapshot, "descriptor_hash")
    assert hasattr(valid_snapshot, "state_hash")
    assert hasattr(valid_snapshot, "state_lookup_hash")
    assert hasattr(valid_snapshot, "descriptor_lookup_hash")
    assert hasattr(valid_snapshot, "dispatcher_lookup_hash")
    assert hasattr(valid_snapshot, "metadata_hash")
    assert hasattr(valid_snapshot, "statistics_hash")
    assert hasattr(valid_snapshot, "dispatcher_hash")

def test_attr_presence_identity_fields(valid_dispatcher):
    assert hasattr(valid_dispatcher.identity, "descriptor")
    assert hasattr(valid_dispatcher.identity, "metadata")
    assert hasattr(valid_dispatcher.identity, "statistics")
    assert hasattr(valid_dispatcher.identity, "snapshot")
    assert hasattr(valid_dispatcher.identity, "runtime_execution_state")
    assert hasattr(valid_dispatcher.identity, "state_lookup")
    assert hasattr(valid_dispatcher.identity, "descriptor_lookup")
    assert hasattr(valid_dispatcher.identity, "dispatcher_lookup")

def test_zero_operational_state():
    assert not hasattr(RuntimeExecutionDispatcher, 'status')
    assert not hasattr(RuntimeExecutionDispatcher, 'dispatch_status')
    assert not hasattr(RuntimeExecutionDispatcher, 'dispatch_state')
    assert not hasattr(RuntimeExecutionDispatcher, 'execution_result')
    assert not hasattr(RuntimeExecutionDispatcherIdentity, 'status')
    assert not hasattr(RuntimeExecutionDispatcherIdentity, 'dispatch_status')

def test_zero_worker_state():
    assert not hasattr(RuntimeExecutionDispatcher, 'worker_state')
    assert not hasattr(RuntimeExecutionDispatcherIdentity, 'worker_state')
    assert not hasattr(RuntimeExecutionDispatcher, 'worker')

def test_zero_queue_state():
    assert not hasattr(RuntimeExecutionDispatcher, 'queue_state')
    assert not hasattr(RuntimeExecutionDispatcherIdentity, 'queue_state')
    assert not hasattr(RuntimeExecutionDispatcher, 'queue')

def test_zero_routing_state():
    assert not hasattr(RuntimeExecutionDispatcher, 'routing_state')
    assert not hasattr(RuntimeExecutionDispatcherIdentity, 'routing_state')
    assert not hasattr(RuntimeExecutionDispatcher, 'route')
    
def test_zero_provider_state():
    assert not hasattr(RuntimeExecutionDispatcher, 'provider_state')
    assert not hasattr(RuntimeExecutionDispatcher, 'provider')

def test_zero_model_state():
    assert not hasattr(RuntimeExecutionDispatcher, 'model_state')
    assert not hasattr(RuntimeExecutionDispatcher, 'model')

def test_zero_monitoring_state():
    assert not hasattr(RuntimeExecutionDispatcher, 'monitoring_state')
    assert not hasattr(RuntimeExecutionDispatcher, 'telemetry_state')

def test_zero_recovery_state():
    assert not hasattr(RuntimeExecutionDispatcher, 'recovery_state')
