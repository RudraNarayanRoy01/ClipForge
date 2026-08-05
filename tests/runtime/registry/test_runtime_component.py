import pytest
from dataclasses import FrozenInstanceError
from backend.src.runtime.registry import (
    RuntimeComponent,
    RuntimeComponentType,
    RuntimeComponentStatus
)

def test_runtime_component_creation():
    comp = RuntimeComponent(
        component_id="core.test.1",
        component_name="Test Core Component",
        component_type=RuntimeComponentType.CORE,
        version="1.0.0",
        description="A test component"
    )
    
    assert comp.component_id == "core.test.1"
    assert comp.component_name == "Test Core Component"
    assert comp.component_type == RuntimeComponentType.CORE
    assert comp.version == "1.0.0"
    assert comp.description == "A test component"
    assert comp.lifecycle_state == "UNKNOWN"
    assert comp.status == RuntimeComponentStatus.UNKNOWN
    assert comp.capabilities == []
    assert comp.tags == []
    assert comp.dependencies == []
    assert comp.metadata == {}

def test_runtime_component_immutability():
    comp = RuntimeComponent(
        component_id="core.test.1",
        component_name="Test Core Component",
        component_type=RuntimeComponentType.CORE,
        version="1.0.0"
    )
    
    with pytest.raises(FrozenInstanceError):
        comp.version = "1.1.0"
