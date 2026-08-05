import pytest
from runtime.services.service_id_factory import ServiceIdFactory
from runtime.services.service_metadata_factory import ServiceMetadataFactory
from runtime.services.runtime_service_factory import RuntimeServiceFactory
from runtime.services import ServiceDescriptor

def test_service_id_factory():
    id1 = ServiceIdFactory.create_id()
    id2 = ServiceIdFactory.create_id()
    assert id1.startswith("svc_comp_")
    assert id2.startswith("svc_comp_")
    assert id1 != id2

def test_service_metadata_factory():
    meta = ServiceMetadataFactory.create(schema_version="2.0", custom_metadata={"env": "test"})
    assert meta.schema_version == "2.0"
    assert meta.builder_version == "1.0.0"
    assert meta.metadata_mapping["env"] == "test"

def test_runtime_service_factory():
    desc = ServiceDescriptor(
        service_id="s1",
        component_id="c1",
        service_name="Test",
        service_type="CORE",
        lifetime="SINGLETON"
    )
    svc = RuntimeServiceFactory.create(desc)
    assert svc.service_id == "s1"
    assert svc.component_id == "c1"
    assert svc.service_name == "Test"
    assert svc.service_type == "CORE"
    assert svc.lifetime == "SINGLETON"
