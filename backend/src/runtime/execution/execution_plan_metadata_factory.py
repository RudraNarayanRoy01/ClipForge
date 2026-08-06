from typing import Dict
from types import MappingProxyType
from .runtime_execution_plan_metadata import RuntimeExecutionPlanMetadata

class ExecutionPlanMetadataFactory:
    
    @classmethod
    def create(cls, 
               labels: Dict[str, str],
               annotations: Dict[str, str],
               tags: Dict[str, str]) -> RuntimeExecutionPlanMetadata:
        return RuntimeExecutionPlanMetadata(
            labels=MappingProxyType(labels.copy()),
            annotations=MappingProxyType(annotations.copy()),
            tags=MappingProxyType(tags.copy())
        )
