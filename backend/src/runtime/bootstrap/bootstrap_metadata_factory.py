"""
Bootstrap Metadata Factory.

Strict SRP factory for generating Bootstrap metadata.
"""
import time
from types import MappingProxyType
from typing import Optional, Dict

from .runtime_bootstrap_metadata import RuntimeBootstrapMetadata


class BootstrapMetadataFactory:
    """
    Factory dedicated exclusively to constructing RuntimeBootstrapMetadata.
    """

    def create_metadata(
        self,
        version: str,
        schema_version: str = "1.0",
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        description: Optional[str] = None
    ) -> RuntimeBootstrapMetadata:
        """Constructs canonical RuntimeBootstrapMetadata."""
        return RuntimeBootstrapMetadata(
            created_at_utc=time.time(),
            version=version,
            schema_version=schema_version,
            labels=MappingProxyType(labels or {}),
            annotations=MappingProxyType(annotations or {}),
            description=description
        )
