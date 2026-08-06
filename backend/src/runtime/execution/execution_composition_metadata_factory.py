from types import MappingProxyType
from typing import Dict, Set, Optional
from .runtime_execution_composition_metadata import RuntimeExecutionCompositionMetadata

class ExecutionCompositionMetadataFactory:
    """
    Performs ONLY structural construction.
    
    NEVER performs:
    - execution
    - lifecycle
    - scheduling
    - provider loading
    - telemetry
    - monitoring
    - optimization
    - planning
    """
    @staticmethod
    def create(
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        tags: Optional[Set[str]] = None
    ) -> RuntimeExecutionCompositionMetadata:
        return RuntimeExecutionCompositionMetadata(
            labels=MappingProxyType(labels.copy() if labels else {}),
            annotations=MappingProxyType(annotations.copy() if annotations else {}),
            tags=frozenset(tags) if tags else frozenset()
        )
