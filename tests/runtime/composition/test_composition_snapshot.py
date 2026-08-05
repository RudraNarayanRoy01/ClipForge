import pytest
from datetime import datetime
from dataclasses import FrozenInstanceError
from backend.src.runtime.composition.composition_snapshot import CompositionSnapshot
from backend.src.runtime.composition.composition_metadata import CompositionMetadata
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from backend.src.runtime.registry.component_types import RuntimeComponentType
from backend.src.runtime.registry.component_status import RuntimeComponentStatus
from backend.src.runtime.dependency.runtime_dependency import RuntimeDependency
from backend.src.runtime.dependency.dependency_type import DependencyType

def test_composition_snapshot_immutability():
    metadata = CompositionMetadata(
        composition_version="1.0",
        schema_version="1.0",
        creation_timestamp=datetime.utcnow(),
        builder_version="1.0"
    )
    
    comp1 = RuntimeComponent(
        component_id="c1",
        component_name="Component1",
        component_type=RuntimeComponentType.CORE,
        version="1.0",
        status=RuntimeComponentStatus.REGISTERED
    )
    
    dep1 = RuntimeDependency(
        dependency_id="d1",
        source_component_id="c1",
        target_component_id="c2",
        dependency_type=DependencyType.REQUIRED
    )
    
    snapshot = CompositionSnapshot(
        components=(comp1,),
        dependencies=(dep1,),
        metadata=metadata,
        timestamp=datetime.utcnow()
    )
    
    with pytest.raises(FrozenInstanceError):
        snapshot.components = ()
        
    with pytest.raises(FrozenInstanceError):
        snapshot.dependencies = ()

def test_composition_snapshot_isolation():
    metadata = CompositionMetadata(
        composition_version="1.0",
        schema_version="1.0",
        creation_timestamp=datetime.utcnow(),
        builder_version="1.0"
    )
    
    snapshot = CompositionSnapshot(
        components=(),
        dependencies=(),
        metadata=metadata,
        timestamp=datetime.utcnow()
    )
    
    assert isinstance(snapshot.components, tuple)
    assert isinstance(snapshot.dependencies, tuple)
