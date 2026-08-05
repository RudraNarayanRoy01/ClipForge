import pytest
from dataclasses import FrozenInstanceError
from backend.src.runtime.dependency import RuntimeDependency, DependencyType

def test_runtime_dependency_immutability():
    dep = RuntimeDependency(
        dependency_id="dep1",
        source_component_id="comp_a",
        target_component_id="comp_b",
        dependency_type=DependencyType.REQUIRED
    )
    
    with pytest.raises(FrozenInstanceError):
        dep.dependency_id = "dep2"

def test_runtime_dependency_creation():
    dep = RuntimeDependency(
        dependency_id="dep1",
        source_component_id="comp_a",
        target_component_id="comp_b",
        dependency_type=DependencyType.OPTIONAL,
        description="Optional dep"
    )
    assert dep.source_component_id == "comp_a"
    assert dep.dependency_type == DependencyType.OPTIONAL
