from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .runtime_execution_composition_descriptor import RuntimeExecutionCompositionDescriptor
from .runtime_execution_composition_metadata import RuntimeExecutionCompositionMetadata
from .runtime_execution_composition_statistics import RuntimeExecutionCompositionStatistics
from .runtime_execution_composition_snapshot import RuntimeExecutionCompositionSnapshot
from .runtime_execution_identity import RuntimeExecutionIdentity
from .runtime_execution_graph import RuntimeExecutionGraph
from .runtime_execution_plan import RuntimeExecutionPlan
from .runtime_execution_context import RuntimeExecutionContext

@dataclass(frozen=True)
class RuntimeExecutionCompositionIdentity:
    descriptor: RuntimeExecutionCompositionDescriptor
    metadata: RuntimeExecutionCompositionMetadata
    statistics: RuntimeExecutionCompositionStatistics
    snapshot: RuntimeExecutionCompositionSnapshot
    execution_identity: RuntimeExecutionIdentity
    execution_graph: RuntimeExecutionGraph
    execution_plan: RuntimeExecutionPlan
    execution_context: RuntimeExecutionContext
    identity_lookup: MappingProxyType[str, RuntimeExecutionIdentity]
    graph_lookup: MappingProxyType[str, RuntimeExecutionGraph]
    plan_lookup: MappingProxyType[str, RuntimeExecutionPlan]
    context_lookup: MappingProxyType[str, RuntimeExecutionContext]
    descriptor_lookup: MappingProxyType[str, RuntimeExecutionCompositionDescriptor]
    composition_lookup: MappingProxyType[str, Any]
