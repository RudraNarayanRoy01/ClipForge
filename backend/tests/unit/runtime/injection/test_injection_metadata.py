import pytest
from types import MappingProxyType
from backend.src.runtime.injection.injection_metadata import InjectionMetadata


def test_metadata_immutability():
    metadata = InjectionMetadata(
        schema_version="1.0",
        builder_version="1.0.0",
        creation_timestamp=12345.6
    )
    with pytest.raises(Exception):
        metadata.schema_version = "2.0"

def test_metadata_initialization():
    metadata = InjectionMetadata(
        schema_version="1.0",
        builder_version="1.0.0",
        creation_timestamp=12345.6,
        metadata_mapping=MappingProxyType({"env": "prod"})
    )
    assert metadata.schema_version == "1.0"
    assert metadata.builder_version == "1.0.0"
    assert metadata.creation_timestamp == 12345.6
    assert metadata.metadata_mapping["env"] == "prod"

def test_metadata_equality():
    m1 = InjectionMetadata("1.0", "1.0.0", 123.0, MappingProxyType({"env": "prod"}))
    m2 = InjectionMetadata("1.0", "1.0.0", 123.0, MappingProxyType({"env": "prod"}))
    assert m1 == m2

