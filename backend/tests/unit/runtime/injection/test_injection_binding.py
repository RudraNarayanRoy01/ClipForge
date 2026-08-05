import pytest
from types import MappingProxyType
from backend.src.runtime.injection.runtime_injection_binding import RuntimeInjectionBinding


def test_binding_immutability():
    binding = RuntimeInjectionBinding(
        interface_id="IMyService",
        implementation_id="MyServiceImpl",
        service_id="service_1",
        lifetime="SINGLETON",
        scope="GLOBAL",
    )
    with pytest.raises(Exception):
        binding.lifetime = "TRANSIENT"

def test_binding_default_collections():
    binding = RuntimeInjectionBinding(
        interface_id="I",
        implementation_id="Impl",
        service_id="s1",
        lifetime="SCOPED",
        scope="REQ"
    )
    assert isinstance(binding.qualifiers, tuple)
    assert len(binding.qualifiers) == 0
    assert isinstance(binding.metadata, MappingProxyType)
    assert len(binding.metadata) == 0

def test_binding_initialization():
    binding = RuntimeInjectionBinding(
        interface_id="I",
        implementation_id="Impl",
        service_id="s1",
        lifetime="SCOPED",
        scope="REQ",
        qualifiers=("db",),
        metadata=MappingProxyType({"version": "1.0"})
    )
    assert binding.interface_id == "I"
    assert binding.implementation_id == "Impl"
    assert binding.service_id == "s1"
    assert binding.lifetime == "SCOPED"
    assert binding.scope == "REQ"
    assert binding.qualifiers == ("db",)
    assert binding.metadata["version"] == "1.0"
