import pytest
from runtime.services import RuntimeServiceBuilder, ServiceDescriptor

def test_builder_successful_composition():
    builder = RuntimeServiceBuilder()
    desc = ServiceDescriptor(
        service_id="s1",
        component_id="c1",
        service_name="Test Service",
        service_type="CORE",
        lifetime="SINGLETON"
    )
    result = builder.build([desc])
    assert result.success is True
    assert result.service_composition is not None
    assert len(result.errors) == 0
    assert result.service_composition.composition_id.startswith("svc_comp_")
    assert len(result.service_composition.services) == 1
    assert result.service_composition.services[0].service_id == "s1"
    assert result.service_composition.statistics.total_services == 1
    assert result.service_composition.snapshot.composition_id == result.service_composition.composition_id

def test_builder_validation_failure():
    builder = RuntimeServiceBuilder()
    desc1 = ServiceDescriptor(service_id="s1", component_id="c1", service_name="N", service_type="T", lifetime="S")
    desc2 = ServiceDescriptor(service_id="s1", component_id="c2", service_name="N", service_type="T", lifetime="S")
    result = builder.build([desc1, desc2])
    assert result.success is False
    assert result.service_composition is None
    assert len(result.errors) > 0

def test_builder_empty_descriptors_yields_warning():
    builder = RuntimeServiceBuilder()
    result = builder.build([])
    assert result.success is True
    assert len(result.warnings) == 1
    assert "Empty" in result.warnings[0]
    assert result.service_composition.statistics.total_services == 0
