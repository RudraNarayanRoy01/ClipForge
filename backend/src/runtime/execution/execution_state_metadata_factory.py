from types import MappingProxyType
from .runtime_execution_state_metadata import RuntimeExecutionStateMetadata

class ExecutionStateMetadataFactory:
    @staticmethod
    def create(
        labels: dict[str, str],
        annotations: dict[str, str],
        tags: set[str]
    ) -> RuntimeExecutionStateMetadata:
        return RuntimeExecutionStateMetadata(
            labels=MappingProxyType(labels.copy()),
            annotations=MappingProxyType(annotations.copy()),
            tags=frozenset(tags)
        )
