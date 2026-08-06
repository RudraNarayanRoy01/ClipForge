from dataclasses import dataclass
from typing import Tuple, Any
from types import MappingProxyType
from .runtime_execution_context_descriptor import RuntimeExecutionContextDescriptor
from .runtime_execution_context_metadata import RuntimeExecutionContextMetadata
from .runtime_execution_variable import RuntimeExecutionVariable
from .runtime_execution_binding import RuntimeExecutionBinding
from .runtime_execution_context_statistics import RuntimeExecutionContextStatistics
from .runtime_execution_context_snapshot import RuntimeExecutionContextSnapshot

@dataclass(frozen=True)
class RuntimeExecutionContextIdentity:
    descriptor: RuntimeExecutionContextDescriptor
    metadata: RuntimeExecutionContextMetadata
    variables: Tuple[RuntimeExecutionVariable, ...]
    bindings: Tuple[RuntimeExecutionBinding, ...]
    statistics: RuntimeExecutionContextStatistics
    snapshot: RuntimeExecutionContextSnapshot
    variable_lookup: MappingProxyType[str, RuntimeExecutionVariable]
    binding_lookup: MappingProxyType[str, RuntimeExecutionBinding]
    descriptor_lookup: MappingProxyType[str, RuntimeExecutionContextDescriptor]
    context_lookup: MappingProxyType[str, Any]
