import pytest
from runtime.services import RuntimeService
from types import MappingProxyType

def test_runtime_service_immutability():
    service = RuntimeService(
        service_id="s1",
        component_id="c1",
        service_name="Test",
        service_type="CORE",
        lifetime="SINGLETON"
    )
    with pytest.raises(Exception):
        service.service_id = "s2"

def test_runtime_service_tuple_conversion():
    service = RuntimeService(
        service_id="s1",
        component_id="c1",
        service_name="Test",
        service_type="CORE",
        lifetime="SINGLETON",
        dependencies=["d1", "d2"],
        tags=["t1"]
    )
    assert isinstance(service.dependencies, tuple)
    assert isinstance(service.tags, tuple)

def test_runtime_service_metadata_mapping():
    service = RuntimeService(
        service_id="s1",
        component_id="c1",
        service_name="Test",
        service_type="CORE",
        lifetime="SINGLETON",
        metadata={"k1": "v1"}
    )
    assert isinstance(service.metadata, MappingProxyType)
    assert service.metadata["k1"] == "v1"

def test_runtime_service_default_factories():
    service = RuntimeService(
        service_id="s1",
        component_id="c1",
        service_name="Test",
        service_type="CORE",
        lifetime="SINGLETON"
    )
    assert service.dependencies == ()
    assert service.tags == ()
    assert isinstance(service.metadata, MappingProxyType)
    assert len(service.metadata) == 0
