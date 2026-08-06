from typing import FrozenSet
from .runtime_execution_graph_metadata import RuntimeExecutionGraphMetadata

class ExecutionGraphMetadataFactory:
    """
    Creates immutable metadata.
    
    Performs NO:
    - execution
    - scheduling
    - provider loading
    - lifecycle
    - dependency injection
    - orchestration
    - planning
    - monitoring
    - optimization
    """
    @staticmethod
    def create_metadata(
        labels: FrozenSet[str] = frozenset(),
        annotations: FrozenSet[str] = frozenset(),
        tags: FrozenSet[str] = frozenset()
    ) -> RuntimeExecutionGraphMetadata:
        return RuntimeExecutionGraphMetadata(
            labels=labels,
            annotations=annotations,
            tags=tags
        )
