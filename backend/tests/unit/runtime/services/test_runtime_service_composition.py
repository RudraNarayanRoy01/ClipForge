import pytest
from types import MappingProxyType
from runtime.services import (
    RuntimeServiceComposition, ValidationResult, ServiceSnapshot,
    RuntimeService, ServiceMetadata, ServiceStatistics
)

def create_dummy_composition():
    svc = RuntimeService(service_id="s1", component_id="c1", service_name="N", service_type="T", lifetime="SINGLETON")
    meta = ServiceMetadata(schema_version="1", builder_version="1")
    stats = ServiceStatistics(1,1,0,0,0,1)
    snapshot = ServiceSnapshot("comp_1", (svc,), meta, stats)
    val = ValidationResult(is_valid=True)
    return RuntimeServiceComposition(
        composition_id="comp_1",
        services=(svc,),
        metadata=meta,
        statistics=stats,
        validation_result=val,
        snapshot=snapshot
    )

def test_composition_immutability():
    comp = create_dummy_composition()
    with pytest.raises(Exception):
        comp.composition_id = "comp_2"

def test_composition_service_map():
    comp = create_dummy_composition()
    assert isinstance(comp.service_map, MappingProxyType)
    assert "s1" in comp.service_map
    assert comp.service_map["s1"].service_id == "s1"
