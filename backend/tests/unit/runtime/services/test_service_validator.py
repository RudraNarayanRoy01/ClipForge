import pytest
from runtime.services import ServiceValidator, ServiceDescriptor
from runtime.services.service_exceptions import (
    DuplicateServiceException, InvalidServiceDescriptorException
)

def test_validator_empty_descriptors():
    result = ServiceValidator.validate_descriptors([])
    assert result.is_valid
    assert len(result.warnings) == 1
    assert "Empty service composition" in result.warnings[0]

def test_validator_missing_service_id():
    desc = ServiceDescriptor(service_id="", component_id="c1", service_name="N", service_type="T", lifetime="SINGLETON")
    result = ServiceValidator.validate_descriptors([desc])
    assert not result.is_valid
    assert any("Missing service identifier" in err for err in result.errors)

def test_validator_duplicate_service_id():
    desc1 = ServiceDescriptor(service_id="s1", component_id="c1", service_name="N1", service_type="T", lifetime="SINGLETON")
    desc2 = ServiceDescriptor(service_id="s1", component_id="c2", service_name="N2", service_type="T", lifetime="SINGLETON")
    result = ServiceValidator.validate_descriptors([desc1, desc2])
    assert not result.is_valid
    assert any("Duplicate service identifier" in err for err in result.errors)

def test_validator_assert_valid_raises():
    desc1 = ServiceDescriptor(service_id="s1", component_id="c1", service_name="N1", service_type="T", lifetime="SINGLETON")
    desc2 = ServiceDescriptor(service_id="s1", component_id="c2", service_name="N2", service_type="T", lifetime="SINGLETON")
    with pytest.raises(DuplicateServiceException):
        ServiceValidator.assert_valid([desc1, desc2])

    desc_missing = ServiceDescriptor(service_id="", component_id="c1", service_name="N", service_type="T", lifetime="SINGLETON")
    with pytest.raises(InvalidServiceDescriptorException):
        ServiceValidator.assert_valid([desc_missing])
