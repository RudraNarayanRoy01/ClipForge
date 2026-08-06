import pytest
from src.runtime.execution import RuntimeExecutionDescriptor

def test_descriptor_creation():
    desc = RuntimeExecutionDescriptor(
        execution_id="exec-123",
        runtime_id="rt-456",
        bootstrap_id="boot-789",
        version="1.0.0",
        schema_version="2.0.0"
    )
    
    assert desc.execution_id == "exec-123"
    assert desc.runtime_id == "rt-456"
    assert desc.bootstrap_id == "boot-789"
    assert desc.version == "1.0.0"
    assert desc.schema_version == "2.0.0"

def test_descriptor_immutability():
    desc = RuntimeExecutionDescriptor("1", "2", "3", "4", "5")
    with pytest.raises(Exception):
        desc.execution_id = "new"
