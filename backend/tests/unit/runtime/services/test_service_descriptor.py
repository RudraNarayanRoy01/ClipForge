import pytest
from runtime.services import ServiceDescriptor
from types import MappingProxyType

def test_service_descriptor_immutability():
    desc = ServiceDescriptor(
        service_id="s1",
        component_id="c1",
        service_name="Test",
        service_type="CORE",
        lifetime="SINGLETON"
    )
    with pytest.raises(Exception):
        desc.service_id = "s2"

def test_service_descriptor_tuple_conversion():
    desc = ServiceDescriptor(
        service_id="s1",
        component_id="c1",
        service_name="Test",
        service_type="CORE",
        lifetime="SINGLETON",
        dependencies=["d1"],
        tags=["t1"]
    )
    assert isinstance(desc.dependencies, tuple)
    assert isinstance(desc.tags, tuple)

def test_service_descriptor_metadata_mapping():
    desc = ServiceDescriptor(
        service_id="s1",
        component_id="c1",
        service_name="Test",
        service_type="CORE",
        lifetime="SINGLETON",
        metadata={"key": "value"}
    )
    assert isinstance(desc.metadata, MappingProxyType)
    assert desc.metadata["key"] == "value"

def test_service_descriptor_defaults():
    desc = ServiceDescriptor(
        service_id="s1",
        component_id="c1",
        service_name="Test",
        service_type="CORE",
        lifetime="SINGLETON"
    )
    assert desc.dependencies == ()
    assert desc.tags == ()
    assert len(desc.metadata) == 0
