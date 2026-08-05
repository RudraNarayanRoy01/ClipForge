import pytest
from backend.src.runtime.injection.injection_descriptor import InjectionDescriptor


def test_descriptor_immutability():
    descriptor = InjectionDescriptor(
        dependency_type="REQUIRED",
        optional=False,
        injection_kind="CONSTRUCTOR",
        scope="GLOBAL",
        target_service="Target",
        dependency_service="Dep"
    )
    with pytest.raises(Exception):
        descriptor.optional = True

def test_descriptor_initialization():
    descriptor = InjectionDescriptor(
        dependency_type="REQUIRED",
        optional=True,
        injection_kind="PROPERTY",
        scope="LOCAL",
        target_service="T1",
        dependency_service="D1",
        qualifier="db"
    )
    assert descriptor.dependency_type == "REQUIRED"
    assert descriptor.optional is True
    assert descriptor.injection_kind == "PROPERTY"
    assert descriptor.scope == "LOCAL"
    assert descriptor.target_service == "T1"
    assert descriptor.dependency_service == "D1"
    assert descriptor.qualifier == "db"

def test_descriptor_default_qualifier():
    descriptor = InjectionDescriptor(
        dependency_type="REQUIRED",
        optional=False,
        injection_kind="CONSTRUCTOR",
        scope="GLOBAL",
        target_service="T1",
        dependency_service="D1"
    )
    assert descriptor.qualifier is None
