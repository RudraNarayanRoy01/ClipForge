from dataclasses import dataclass
from typing import Tuple, Any
from types import MappingProxyType
from .runtime_execution_plan_descriptor import RuntimeExecutionPlanDescriptor
from .runtime_execution_plan_metadata import RuntimeExecutionPlanMetadata
from .runtime_execution_plan_statistics import RuntimeExecutionPlanStatistics
from .runtime_execution_plan_snapshot import RuntimeExecutionPlanSnapshot
from .runtime_execution_layer import RuntimeExecutionLayer
from .runtime_execution_dependency_batch import RuntimeExecutionDependencyBatch

@dataclass(frozen=True)
class RuntimeExecutionPlanIdentity:
    descriptor: RuntimeExecutionPlanDescriptor
    metadata: RuntimeExecutionPlanMetadata
    statistics: RuntimeExecutionPlanStatistics
    snapshot: RuntimeExecutionPlanSnapshot
    layers: Tuple[RuntimeExecutionLayer, ...]
    layer_lookup: MappingProxyType[str, RuntimeExecutionLayer]
    batch_lookup: MappingProxyType[str, RuntimeExecutionDependencyBatch]
    descriptor_lookup: MappingProxyType[str, RuntimeExecutionPlanDescriptor]
    plan_lookup: MappingProxyType[str, Any]
