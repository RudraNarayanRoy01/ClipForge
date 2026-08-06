import pytest
from src.runtime.execution import (
    ExecutionIdFactory,
    ExecutionMetadataFactory,
    ExecutionSnapshotFactory,
    RuntimeExecutionFactory,
    RuntimeExecutionDescriptor,
    RuntimeExecutionState,
    RuntimeExecutionIdentity,
    ExecutionStage
)

def test_execution_id_factory():
    exec_id = ExecutionIdFactory.generate_execution_id()
    assert exec_id.startswith("exec-")
    assert len(exec_id) > 10

def test_metadata_factory():
    meta = ExecutionMetadataFactory.create_metadata(
        name="Test",
        description="Desc",
        tags=["a", "b"],
        annotations={"k": "v"}
    )
    assert meta.name == "Test"
    assert meta.description == "Desc"
    assert "a" in meta.tags
    assert meta.annotations["k"] == "v"
    assert meta.metadata_version == "1.0.0"

def test_snapshot_factory():
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    state = RuntimeExecutionState(ExecutionStage.READY)
    
    snap = ExecutionSnapshotFactory.create_snapshot(desc, meta, state, "comp_hash_123")
    assert snap.execution_hash
    assert snap.identity_hash
    assert snap.descriptor_hash
    assert snap.metadata_hash
    assert snap.state_hash
    assert snap.composition_hash == "comp_hash_123"

def test_execution_factory():
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    state = RuntimeExecutionState(ExecutionStage.READY)
    snap = ExecutionSnapshotFactory.create_snapshot(desc, meta, state, "comp_hash_123")
    
    identity = RuntimeExecutionIdentity(desc, meta, state, snap)
    
    exec_obj = RuntimeExecutionFactory.create_execution("exec-1", identity)
    assert exec_obj.identifier == "exec-1"
    assert exec_obj.identity == identity
