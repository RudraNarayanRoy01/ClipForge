import pytest
from src.runtime.execution import (
    ExecutionMetadataFactory,
    ExecutionSnapshotFactory,
    RuntimeExecutionDescriptor,
    RuntimeExecutionState,
    ExecutionStage
)

def test_metadata_factory_empty_collections():
    meta = ExecutionMetadataFactory.create_metadata("Test")
    assert len(meta.tags) == 0
    assert len(meta.annotations) == 0
    assert isinstance(meta.tags, frozenset)

def test_snapshot_factory_determinism():
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    state = RuntimeExecutionState(ExecutionStage.READY)
    
    snap1 = ExecutionSnapshotFactory.create_snapshot(desc, meta, state, "comp_hash_123")
    snap2 = ExecutionSnapshotFactory.create_snapshot(desc, meta, state, "comp_hash_123")
    
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
    state = RuntimeExecutionState(ExecutionStage.READY)
    
    snap1 = ExecutionSnapshotFactory.create_snapshot(desc1, meta, state, "comp_hash_123")
    snap2 = ExecutionSnapshotFactory.create_snapshot(desc2, meta, state, "comp_hash_123")
    
    assert snap1.descriptor_hash != snap2.descriptor_hash
    assert snap1.execution_hash != snap2.execution_hash

def test_snapshot_factory_hash_changes_with_metadata():
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta1 = ExecutionMetadataFactory.create_metadata("Test")
    meta2 = ExecutionMetadataFactory.create_metadata("Test-mod")
    state = RuntimeExecutionState(ExecutionStage.READY)
    
    snap1 = ExecutionSnapshotFactory.create_snapshot(desc, meta1, state, "comp_hash_123")
    snap2 = ExecutionSnapshotFactory.create_snapshot(desc, meta2, state, "comp_hash_123")
    
    assert snap1.metadata_hash != snap2.metadata_hash
    assert snap1.execution_hash != snap2.execution_hash

def test_snapshot_factory_hash_changes_with_state():
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    state1 = RuntimeExecutionState(ExecutionStage.READY)
    state2 = RuntimeExecutionState(ExecutionStage.VALIDATED)
    
    snap1 = ExecutionSnapshotFactory.create_snapshot(desc, meta, state1, "comp_hash_123")
    snap2 = ExecutionSnapshotFactory.create_snapshot(desc, meta, state2, "comp_hash_123")
    
    assert snap1.state_hash != snap2.state_hash
    assert snap1.execution_hash != snap2.execution_hash

def test_snapshot_factory_hash_changes_with_composition():
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    state = RuntimeExecutionState(ExecutionStage.READY)
    
    snap1 = ExecutionSnapshotFactory.create_snapshot(desc, meta, state, "comp_hash_1")
    snap2 = ExecutionSnapshotFactory.create_snapshot(desc, meta, state, "comp_hash_2")
    
    assert snap1.composition_hash != snap2.composition_hash
    assert snap1.execution_hash != snap2.execution_hash

def test_state_enum_members():
    assert ExecutionStage.UNINITIALIZED.name == "UNINITIALIZED"
    assert ExecutionStage.PREPARED.name == "PREPARED"
    assert ExecutionStage.VALIDATED.name == "VALIDATED"
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
    state = RuntimeExecutionState(ExecutionStage.READY)
    snap = ExecutionSnapshotFactory.create_snapshot(desc, meta, state, "comp")
    
    identity = RuntimeExecutionIdentity(desc, meta, state, snap)
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
    state = RuntimeExecutionState(ExecutionStage.READY)
    snap = RuntimeExecutionSnapshot("a", "b", "c", "d", "e", "f")
    
    identity = RuntimeExecutionIdentity(desc, meta, state, snap)
    assert identity.descriptor == desc
    assert identity.metadata == meta
    assert identity.state == state
    assert identity.snapshot == snap

def test_execution_identity_immutability():
    from src.runtime.execution import RuntimeExecutionIdentity, RuntimeExecutionSnapshot
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    meta = ExecutionMetadataFactory.create_metadata("Test")
    state = RuntimeExecutionState(ExecutionStage.READY)
    snap = RuntimeExecutionSnapshot("a", "b", "c", "d", "e", "f")
    identity = RuntimeExecutionIdentity(desc, meta, state, snap)
    
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
    state = RuntimeExecutionState(ExecutionStage.READY)
    
    snap1 = ExecutionSnapshotFactory.create_snapshot(desc, meta, state, "comp")
    snap2 = ExecutionSnapshotFactory.create_snapshot(desc, meta, state, "comp")
    
    assert snap1.identity_hash == snap2.identity_hash
    assert snap1.execution_hash == snap2.execution_hash


