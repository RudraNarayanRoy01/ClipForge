"""
Injection Metadata Factory.

SRP-compliant factory for generating immutable injection metadata.
"""
import time

from .injection_metadata import InjectionMetadata


class InjectionMetadataFactory:
    """Creates immutable injection metadata."""
    
    def create(self, builder_version: str = "1.0.0") -> InjectionMetadata:
        """Generates the metadata instance."""
        return InjectionMetadata(
            schema_version="1.0",
            builder_version=builder_version,
            creation_timestamp=time.time(),
        )
