import pytest
from runtime.services import ServiceMetadata
from types import MappingProxyType

def test_service_metadata_immutability():
    meta = ServiceMetadata(schema_version="1.0", builder_version="2.0")
    with pytest.raises(Exception):
        meta.schema_version = "1.1"

def test_service_metadata_mapping_proxy():
    meta = ServiceMetadata(
        schema_version="1.0", 
        builder_version="2.0", 
        metadata_mapping={"a": 1}
    )
    assert isinstance(meta.metadata_mapping, MappingProxyType)
    with pytest.raises(TypeError):
        meta.metadata_mapping["a"] = 2

def test_service_metadata_defaults():
    meta = ServiceMetadata(schema_version="1.0", builder_version="1.0")
    assert meta.creation_timestamp > 0
    assert isinstance(meta.metadata_mapping, MappingProxyType)
    assert len(meta.metadata_mapping) == 0
