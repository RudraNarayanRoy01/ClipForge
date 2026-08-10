import pytest
from src.runtime.execution import (
    ExecutionMetadataFactory,
    ExecutionSnapshotFactory,
    RuntimeExecutionDescriptor,
    ExecutionStage
)
from src.runtime.domain.runtime_execution_model import RuntimeExecutionStatus

def test_metadata_factory_empty_collections():
    meta = ExecutionMetadataFactory.create_metadata("Test")
    assert len(meta.tags) == 0
    assert len(meta.annotations) == 0
    assert isinstance(meta.tags, frozenset)

def test_snapshot_factory_determinism():
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    status = RuntimeExecutionStatus.READY
    
    snap1 = ExecutionSnapshotFactory.create_snapshot(desc, meta, status, "comp_hash_123")
    snap2 = ExecutionSnapshotFactory.create_snapshot(desc, meta, status, "comp_hash_123")
    
    assert snap1.execution_hash == snap2.execution_hash
    assert snap1.descriptor_hash == snap2.descriptor_hash
    assert snap1.metadata_hash == snap2.metadata_hash
    assert snap1.state_hash == snap2.state_hash

def test_execution_snapshot_with_missing_descriptor_fields():
    with pytest.raises(TypeError):
        # Missing execution_id
        RuntimeExecutionDescriptor(runtime_id="1", bootstrap_id="2", version="3", schema_version="4")

def test_execution_metadata_with_invalid_types():
    with pytest.raises(TypeError):
        # Missing required name argument
        ExecutionMetadataFactory.create_metadata()


def test_snapshot_factory_hash_changes_with_descriptor():
    desc1 = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    desc2 = RuntimeExecutionDescriptor("1-mod", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    status = RuntimeExecutionStatus.READY
    
    snap1 = ExecutionSnapshotFactory.create_snapshot(desc1, meta, status, "comp_hash_123")
    snap2 = ExecutionSnapshotFactory.create_snapshot(desc2, meta, status, "comp_hash_123")
    
    assert snap1.descriptor_hash != snap2.descriptor_hash
    assert snap1.execution_hash != snap2.execution_hash

def test_snapshot_factory_hash_changes_with_metadata():
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta1 = ExecutionMetadataFactory.create_metadata("Test")
    meta2 = ExecutionMetadataFactory.create_metadata("Test-mod")
    status = RuntimeExecutionStatus.READY
    
    snap1 = ExecutionSnapshotFactory.create_snapshot(desc, meta1, status, "comp_hash_123")
    snap2 = ExecutionSnapshotFactory.create_snapshot(desc, meta2, status, "comp_hash_123")
    
    assert snap1.metadata_hash != snap2.metadata_hash
    assert snap1.execution_hash != snap2.execution_hash

def test_snapshot_factory_hash_changes_with_state():
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    status1 = RuntimeExecutionStatus.READY
    status2 = RuntimeExecutionStatus.PREPARED
    
    snap1 = ExecutionSnapshotFactory.create_snapshot(desc, meta, status1, "comp_hash_123")
    snap2 = ExecutionSnapshotFactory.create_snapshot(desc, meta, status2, "comp_hash_123")
    
    assert snap1.state_hash != snap2.state_hash
    assert snap1.execution_hash != snap2.execution_hash

def test_snapshot_factory_hash_changes_with_composition():
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    status = RuntimeExecutionStatus.READY
    
    snap1 = ExecutionSnapshotFactory.create_snapshot(desc, meta, status, "comp_hash_1")
    snap2 = ExecutionSnapshotFactory.create_snapshot(desc, meta, status, "comp_hash_2")
    
    assert snap1.composition_hash != snap2.composition_hash
    assert snap1.execution_hash != snap2.execution_hash

def test_state_enum_members():
    assert RuntimeExecutionStatus.PREPARED.name == "PREPARED"
    assert RuntimeExecutionStatus.READY.name == "READY"
    assert ExecutionStage.READY.name == "READY"
    assert len(ExecutionStage) == 4

def test_exceptions_hierarchy():
    from src.runtime.execution import (
        RuntimeExecutionException,
        ExecutionValidationException,
        ExecutionMetadataException,
        ExecutionSnapshotException,
        ExecutionStateException
    )
    assert issubclass(ExecutionValidationException, RuntimeExecutionException)
    assert issubclass(ExecutionMetadataException, RuntimeExecutionException)
    assert issubclass(ExecutionSnapshotException, RuntimeExecutionException)
    assert issubclass(ExecutionStateException, RuntimeExecutionException)
    assert issubclass(RuntimeExecutionException, Exception)

def test_result_creation():
    from src.runtime.execution import RuntimeExecutionResult, RuntimeExecutionException, RuntimeExecutionFactory, RuntimeExecutionIdentity
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    status = RuntimeExecutionStatus.READY
    snap = ExecutionSnapshotFactory.create_snapshot(desc, meta, status, "comp")
    
    identity = RuntimeExecutionIdentity(desc, meta, status, snap)
    exec_obj = RuntimeExecutionFactory.create_execution("exec-1", identity)
    
    warns = ("warning 1", "warning 2")
    errs = (RuntimeExecutionException("err 1"),)
    
    res = RuntimeExecutionResult(exec_obj, snap, warns, errs)
    
    assert res.execution == exec_obj
    assert res.snapshot == snap
    assert res.warnings == warns
    assert res.errors == errs

def test_result_immutability():
    from src.runtime.execution import RuntimeExecutionResult
    with pytest.raises(TypeError):
        # Result needs all args
        RuntimeExecutionResult()

def test_execution_identity_creation():
    from src.runtime.execution import RuntimeExecutionIdentity, RuntimeExecutionSnapshot
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    status = RuntimeExecutionStatus.READY
    snap = RuntimeExecutionSnapshot("a", "b", "c", "d", "e", "f")
    
    identity = RuntimeExecutionIdentity(desc, meta, status, snap)
    assert identity.descriptor == desc
    assert identity.metadata == meta
    assert identity.status == status
    assert identity.snapshot == snap

def test_execution_identity_immutability():
    from src.runtime.execution import RuntimeExecutionIdentity, RuntimeExecutionSnapshot
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    status = RuntimeExecutionStatus.READY
    snap = RuntimeExecutionSnapshot("a", "b", "c", "d", "e", "f")
    identity = RuntimeExecutionIdentity(desc, meta, status, snap)
    
    with pytest.raises(Exception):
        identity.descriptor = None

def test_mapping_proxy_protection():
    meta = ExecutionMetadataFactory.create_metadata("Test", annotations={"key": "value"})
    with pytest.raises(Exception):
        meta.annotations["key"] = "new_value"

def test_frozenset_protection():
    meta = ExecutionMetadataFactory.create_metadata("Test", tags=["tag1"])
    with pytest.raises(Exception):
        meta.tags.add("tag2")

def test_identity_hash_determinism():
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    status = RuntimeExecutionStatus.READY
    
    snap1 = ExecutionSnapshotFactory.create_snapshot(desc, meta, status, "comp")
    snap2 = ExecutionSnapshotFactory.create_snapshot(desc, meta, status, "comp")
    
    assert snap1.identity_hash == snap2.identity_hash
    assert snap1.execution_hash == snap2.execution_hash


