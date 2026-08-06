import pytest
from types import MappingProxyType
from datetime import datetime, timezone
from src.runtime.execution import RuntimeExecutionMetadata

def test_metadata_creation():
    now = datetime.now(timezone.utc)
    tags = frozenset(["fast", "priority"])
    ann = MappingProxyType({"env": "prod"})
    
    meta = RuntimeExecutionMetadata(
        name="Main Execution",
        description="The primary execution path",
        created_at=now,
        updated_at=now,
        tags=tags,
        annotations=ann,
        metadata_version="1.5.0"
    )
    
    assert meta.name == "Main Execution"
    assert meta.description == "The primary execution path"
    assert meta.created_at == now
    assert meta.updated_at == now
    assert meta.tags == tags
    assert meta.annotations == ann
    assert meta.metadata_version == "1.5.0"

def test_metadata_immutability():
    now = datetime.now(timezone.utc)
    meta = RuntimeExecutionMetadata("A", "B", now, now, frozenset(), MappingProxyType({}), "1")
    with pytest.raises(Exception):
        meta.name = "new"
