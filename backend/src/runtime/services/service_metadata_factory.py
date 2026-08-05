"""
Factory for Service Metadata.
"""
from typing import Mapping, Any
from types import MappingProxyType
from datetime import datetime, timezone
from .service_metadata import ServiceMetadata

class ServiceMetadataFactory:
    """Creates immutable composition metadata."""
    
    @staticmethod
    def create(schema_version: str = "1.0.0", builder_version: str = "1.0.0", custom_metadata: Mapping[str, Any] = None) -> ServiceMetadata:
        mapping = custom_metadata if custom_metadata else {}
        return ServiceMetadata(
            schema_version=schema_version,
            builder_version=builder_version,
            creation_timestamp=datetime.now(timezone.utc).timestamp(),
            metadata_mapping=MappingProxyType(dict(mapping))
        )
