import pytest
from datetime import datetime
from backend.src.runtime.composition.composition_snapshot_factory import CompositionSnapshotFactory
from backend.src.runtime.composition.composition_metadata_factory import CompositionMetadataFactory
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from backend.src.runtime.registry.component_types import RuntimeComponentType
from backend.src.runtime.registry.component_status import RuntimeComponentStatus
from backend.src.runtime.dependency.runtime_dependency import RuntimeDependency
from backend.src.runtime.dependency.dependency_type import DependencyType

def test_snapshot_factory_create():
    metadata = CompositionMetadataFactory.create()
    
    comp1 = RuntimeComponent("c1", "Comp1", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED)
    dep1 = RuntimeDependency("d1", "c1", "c2", DependencyType.REQUIRED)
    
    components = (comp1,)
    dependencies = (dep1,)
    
    snapshot = CompositionSnapshotFactory.create(components, dependencies, metadata)
    
    assert snapshot.components == components
    assert snapshot.dependencies == dependencies
    assert snapshot.metadata == metadata
    assert snapshot.timestamp == metadata.creation_timestamp
