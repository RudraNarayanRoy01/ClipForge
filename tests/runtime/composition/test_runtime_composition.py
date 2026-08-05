import pytest
from datetime import datetime
from dataclasses import FrozenInstanceError
from backend.src.runtime.composition.runtime_composition import RuntimeComposition
from backend.src.runtime.composition.composition_metadata import CompositionMetadata
from backend.src.runtime.composition.composition_statistics import CompositionStatistics
from backend.src.runtime.composition.composition_snapshot import CompositionSnapshot
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from backend.src.runtime.registry.component_types import RuntimeComponentType
from backend.src.runtime.registry.component_status import RuntimeComponentStatus

def test_runtime_composition_immutability():
    metadata = CompositionMetadata(
        composition_version="1.0",
        schema_version="1.0",
        creation_timestamp=datetime.utcnow(),
        builder_version="1.0"
    )
    
    stats = CompositionStatistics(0, 0, 0, 0, 0)
    
    comp = RuntimeComposition(
        composition_id="comp-1",
        components=(),
        dependencies=(),
        metadata=metadata,
        statistics=stats
    )
    
    with pytest.raises(FrozenInstanceError):
        comp.composition_id = "comp-2"

def test_runtime_composition_get_snapshot():
    metadata = CompositionMetadata(
        composition_version="1.0",
        schema_version="1.0",
        creation_timestamp=datetime.utcnow(),
        builder_version="1.0"
    )
    
    stats = CompositionStatistics(0, 0, 0, 0, 0)
    
    comp = RuntimeComposition(
        composition_id="comp-1",
        components=(),
        dependencies=(),
        metadata=metadata,
        statistics=stats
    )
    
    snapshot = comp.get_snapshot()
    assert isinstance(snapshot, CompositionSnapshot)
    assert snapshot.components == comp.components
    assert snapshot.dependencies == comp.dependencies
    assert snapshot.metadata == comp.metadata
    assert snapshot.timestamp == comp.metadata.creation_timestamp

def test_runtime_composition_ordering():
    comp1 = RuntimeComponent(
        component_id="c1",
        component_name="Component1",
        component_type=RuntimeComponentType.CORE,
        version="1.0",
        status=RuntimeComponentStatus.REGISTERED
    )
    comp2 = RuntimeComponent(
        component_id="c2",
        component_name="Component2",
        component_type=RuntimeComponentType.CORE,
        version="1.0",
        status=RuntimeComponentStatus.REGISTERED
    )
    
    metadata = CompositionMetadata(
        composition_version="1.0",
        schema_version="1.0",
        creation_timestamp=datetime.utcnow(),
        builder_version="1.0"
    )
    stats = CompositionStatistics(2, 0, 2, 2, 0)
    
    comp = RuntimeComposition(
        composition_id="comp-1",
        components=(comp1, comp2),
        dependencies=(),
        metadata=metadata,
        statistics=stats
    )
    
    assert comp.components[0].component_id == "c1"
    assert comp.components[1].component_id == "c2"
