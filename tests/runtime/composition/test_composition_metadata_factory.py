import pytest
from datetime import datetime
from backend.src.runtime.composition.composition_metadata_factory import CompositionMetadataFactory
from backend.src.runtime.composition.composition_metadata import CompositionMetadata

def test_metadata_factory_create():
    metadata = CompositionMetadataFactory.create(
        builder_version="1.1.0",
        schema_version="2.0.0",
        composition_version="1.5.0"
    )
    
    assert isinstance(metadata, CompositionMetadata)
    assert metadata.builder_version == "1.1.0"
    assert metadata.schema_version == "2.0.0"
    assert metadata.composition_version == "1.5.0"
    assert isinstance(metadata.creation_timestamp, datetime)
