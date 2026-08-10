from types import MappingProxyType
from typing import Dict, Set
from .runtime_execution_dispatcher_metadata import RuntimeExecutionDispatcherMetadata

class ExecutionDispatcherMetadataFactory:
    @staticmethod
    def create(
        labels: Dict[str, str],
        annotations: Dict[str, str],
        tags: Set[str]
    ) -> RuntimeExecutionDispatcherMetadata:
        return RuntimeExecutionDispatcherMetadata(
            labels=MappingProxyType(labels.copy()),
            annotations=MappingProxyType(annotations.copy()),
            tags=frozenset(tags)
        )
