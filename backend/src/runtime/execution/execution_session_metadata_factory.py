from types import MappingProxyType
from typing import Mapping, Iterable
from .runtime_execution_session_metadata import RuntimeExecutionSessionMetadata

class ExecutionSessionMetadataFactory:
    @staticmethod
    def create(
        labels: Mapping[str, str],
        annotations: Mapping[str, str],
        tags: Iterable[str]
    ) -> RuntimeExecutionSessionMetadata:
        return RuntimeExecutionSessionMetadata(
            labels=MappingProxyType(dict(labels)),
            annotations=MappingProxyType(dict(annotations)),
            tags=frozenset(tags)
        )
