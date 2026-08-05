import pytest
import time
from dataclasses import FrozenInstanceError

from backend.src.runtime.registry import (
    RuntimeComponentRegistry,
    RuntimeComponent,
    RuntimeComponentType,
    RuntimeComponentStatus,
    DuplicateComponentException,
    UnknownComponentException,
    RegistryFrozenException,
    InvalidComponentException,
    RegistryConsistencyException
)

@pytest.fixture
def empty_registry():
    return RuntimeComponentRegistry()

@pytest.fixture
def sample_component():
    return RuntimeComponent(
        component_id="core.test.1",
        component_name="Test Core Component",
        component_type=RuntimeComponentType.CORE,
        version="1.0.0"
    )

@pytest.fixture
def sample_component_2():
    return RuntimeComponent(
        component_id="monitor.test.1",
        component_name="Test Monitor Component",
        component_type=RuntimeComponentType.MONITORING,
        version="1.0.0"
    )

def test_registry_starts_empty(empty_registry):
    assert empty_registry.get_statistics().total_components == 0
    assert len(empty_registry.enumerate_components()) == 0

def test_successful_registration(empty_registry, sample_component):
    result = empty_registry.register(sample_component)
    assert result.success is True
    assert result.registered_component == sample_component
    assert empty_registry.get_by_id(sample_component.component_id) == sample_component
    assert empty_registry.get_by_name(sample_component.component_name) == sample_component
    assert empty_registry.get_statistics().total_components == 1

def test_duplicate_id_rejection(empty_registry, sample_component):
    empty_registry.register(sample_component)
    duplicate_id_comp = RuntimeComponent(
        component_id=sample_component.component_id,
        component_name="Different Name",
        component_type=RuntimeComponentType.CORE,
        version="1.0.0"
    )
    with pytest.raises(DuplicateComponentException):
        empty_registry.register(duplicate_id_comp)

def test_duplicate_name_rejection(empty_registry, sample_component):
    empty_registry.register(sample_component)
    duplicate_name_comp = RuntimeComponent(
        component_id="different.id",
        component_name=sample_component.component_name,
        component_type=RuntimeComponentType.CORE,
        version="1.0.0"
    )
    with pytest.raises(DuplicateComponentException):
        empty_registry.register(duplicate_name_comp)

def test_invalid_component_rejection_missing_id(empty_registry):
    invalid_comp = RuntimeComponent(
        component_id="",
        component_name="Some Name",
        component_type=RuntimeComponentType.CORE,
        version="1.0.0"
    )
    with pytest.raises(InvalidComponentException):
        empty_registry.register(invalid_comp)

def test_invalid_component_rejection_missing_name(empty_registry):
    invalid_comp = RuntimeComponent(
        component_id="some.id",
        component_name="",
        component_type=RuntimeComponentType.CORE,
        version="1.0.0"
    )
    with pytest.raises(InvalidComponentException):
        empty_registry.register(invalid_comp)

def test_invalid_component_rejection_missing_type(empty_registry):
    invalid_comp = RuntimeComponent(
        component_id="some.id",
        component_name="Some Name",
        component_type=None,
        version="1.0.0"
    )
    with pytest.raises(InvalidComponentException):
        empty_registry.register(invalid_comp)

def test_invalid_component_rejection_missing_version(empty_registry):
    invalid_comp = RuntimeComponent(
        component_id="some.id",
        component_name="Some Name",
        component_type=RuntimeComponentType.CORE,
        version=""
    )
    with pytest.raises(InvalidComponentException):
        empty_registry.register(invalid_comp)

def test_frozen_registry_rejection(empty_registry, sample_component):
    empty_registry.freeze()
    assert empty_registry.is_frozen() is True
    with pytest.raises(RegistryFrozenException):
        empty_registry.register(sample_component)

def test_freeze_already_frozen_registry(empty_registry):
    empty_registry.freeze()
    assert empty_registry.is_frozen() is True
    # Should not raise exception
    empty_registry.freeze()
    assert empty_registry.is_frozen() is True

def test_frozen_registry_remove_rejection(empty_registry, sample_component):
    empty_registry.register(sample_component)
    empty_registry.freeze()
    with pytest.raises(RegistryFrozenException):
        empty_registry.remove(sample_component.component_id)

def test_lookup_by_id(empty_registry, sample_component):
    empty_registry.register(sample_component)
    comp = empty_registry.get_by_id(sample_component.component_id)
    assert comp.component_id == sample_component.component_id

def test_lookup_by_name(empty_registry, sample_component):
    empty_registry.register(sample_component)
    comp = empty_registry.get_by_name(sample_component.component_name)
    assert comp.component_name == sample_component.component_name

def test_unknown_component_lookup(empty_registry):
    with pytest.raises(UnknownComponentException):
        empty_registry.get_by_id("non.existent")
    
    with pytest.raises(UnknownComponentException):
        empty_registry.get_by_name("Non Existent Name")

def test_remove_component(empty_registry, sample_component):
    empty_registry.register(sample_component)
    empty_registry.remove(sample_component.component_id)
    assert empty_registry.get_statistics().total_components == 0
    with pytest.raises(UnknownComponentException):
        empty_registry.get_by_id(sample_component.component_id)

def test_remove_unknown_component(empty_registry):
    with pytest.raises(UnknownComponentException):
        empty_registry.remove("non.existent")

def test_remove_re_register_sequence(empty_registry, sample_component):
    empty_registry.register(sample_component)
    empty_registry.remove(sample_component.component_id)
    # Should be able to register it again
    result = empty_registry.register(sample_component)
    assert result.success is True
    assert empty_registry.get_statistics().total_components == 1
    assert empty_registry.get_by_id(sample_component.component_id) == sample_component

def test_enumeration_and_ordering(empty_registry, sample_component, sample_component_2):
    empty_registry.register(sample_component)
    empty_registry.register(sample_component_2)
    
    components = empty_registry.enumerate_components()
    assert len(components) == 2
    assert components[0].component_id == sample_component.component_id
    assert components[1].component_id == sample_component_2.component_id
    
    # list_components should delegate to enumerate_components
    assert empty_registry.list_components() == components

def test_deterministic_ordering_multiple_ops(empty_registry, sample_component, sample_component_2):
    empty_registry.register(sample_component)
    empty_registry.register(sample_component_2)
    empty_registry.remove(sample_component.component_id)
    
    components = empty_registry.enumerate_components()
    assert len(components) == 1
    assert components[0].component_id == sample_component_2.component_id
    
    # Registering again should put it at the end
    empty_registry.register(sample_component)
    components2 = empty_registry.enumerate_components()
    assert len(components2) == 2
    assert components2[0].component_id == sample_component_2.component_id
    assert components2[1].component_id == sample_component.component_id

def test_snapshot_immutability(empty_registry, sample_component, sample_component_2):
    empty_registry.register(sample_component)
    snapshot = empty_registry.get_snapshot()
    
    assert snapshot.component_count == 1
    assert snapshot.components[0].component_id == sample_component.component_id
    
    empty_registry.register(sample_component_2)
    
    # Snapshot should remain unaffected
    assert snapshot.component_count == 1
    assert len(empty_registry.enumerate_components()) == 2
    
    # Trying to modify snapshot components should fail (tuple is immutable)
    with pytest.raises(TypeError):
        snapshot.components[0] = sample_component_2

def test_snapshot_unaffected_by_remove(empty_registry, sample_component):
    empty_registry.register(sample_component)
    snapshot = empty_registry.get_snapshot()
    
    empty_registry.remove(sample_component.component_id)
    
    # Registry is empty
    assert empty_registry.get_statistics().total_components == 0
    # Snapshot still has it
    assert snapshot.component_count == 1
    assert snapshot.components[0].component_id == sample_component.component_id

def test_statistics(empty_registry, sample_component, sample_component_2):
    empty_registry.register(sample_component)
    empty_registry.register(sample_component_2)
    
    stats = empty_registry.get_statistics()
    
    assert stats.total_components == 2
    assert stats.components_by_type[RuntimeComponentType.CORE] == 1
    assert stats.components_by_type[RuntimeComponentType.MONITORING] == 1
    assert stats.components_by_status[RuntimeComponentStatus.UNKNOWN] == 2
    assert stats.registration_order == (sample_component.component_id, sample_component_2.component_id)

def test_statistics_after_remove(empty_registry, sample_component, sample_component_2):
    empty_registry.register(sample_component)
    empty_registry.register(sample_component_2)
    empty_registry.remove(sample_component.component_id)
    
    stats = empty_registry.get_statistics()
    
    assert stats.total_components == 1
    # CORE component was removed, should not be in counts or it might be missing
    assert stats.components_by_type.get(RuntimeComponentType.CORE, 0) == 0
    assert stats.components_by_type[RuntimeComponentType.MONITORING] == 1
    assert stats.registration_order == (sample_component_2.component_id,)
