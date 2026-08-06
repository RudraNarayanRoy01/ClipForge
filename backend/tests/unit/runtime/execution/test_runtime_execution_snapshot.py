import pytest
from src.runtime.execution import RuntimeExecutionSnapshot

def test_snapshot_creation():
    snap = RuntimeExecutionSnapshot(
        execution_hash="exec_hash",
        identity_hash="ident_hash",
        descriptor_hash="desc_hash",
        metadata_hash="meta_hash",
        state_hash="state_hash",
        composition_hash="comp_hash"
    )
    
    assert snap.execution_hash == "exec_hash"
    assert snap.identity_hash == "ident_hash"
    assert snap.descriptor_hash == "desc_hash"
    assert snap.metadata_hash == "meta_hash"
    assert snap.state_hash == "state_hash"
    assert snap.composition_hash == "comp_hash"

def test_snapshot_immutability():
    snap = RuntimeExecutionSnapshot("1", "2", "3", "4", "5", "6")
    with pytest.raises(Exception):
        snap.execution_hash = "new"
