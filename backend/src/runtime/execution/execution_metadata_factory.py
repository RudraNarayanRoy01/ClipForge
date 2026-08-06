from datetime import datetime, timezone
from types import MappingProxyType
from typing import Iterable, Mapping, Optional
from .runtime_execution_metadata import RuntimeExecutionMetadata

class ExecutionMetadataFactory:
    @staticmethod
    def create_metadata(
        name: str,
        description: str = "",
        tags: Optional[Iterable[str]] = None,
        annotations: Optional[Mapping[str, str]] = None,
        metadata_version: str = "1.0.0"
    ) -> RuntimeExecutionMetadata:
        now = datetime.now(timezone.utc)
        return RuntimeExecutionMetadata(
            name=name,
            description=description,
            created_at=now,
            updated_at=now,
            tags=frozenset(tags) if tags else frozenset(),
            annotations=MappingProxyType(dict(annotations)) if annotations else MappingProxyType({}),
            metadata_version=metadata_version
        )
