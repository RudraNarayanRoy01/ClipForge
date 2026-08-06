from typing import Tuple, Any
from types import MappingProxyType
from .runtime_execution_variable import RuntimeExecutionVariable
from .runtime_execution_binding import RuntimeExecutionBinding
from .runtime_execution_context_descriptor import RuntimeExecutionContextDescriptor
from .runtime_execution_context_statistics import RuntimeExecutionContextStatistics

class ExecutionContextStatisticsBuilder:
    """
    Builds context statistics structurally.
    
    Performs NO:
    - Execution
    - Scheduling
    - Provider Loading
    - Lifecycle
    - Optimization
    - Telemetry
    - Monitoring
    - Planning
    """
    @staticmethod
    def build(
        variables: Tuple[RuntimeExecutionVariable, ...],
        bindings: Tuple[RuntimeExecutionBinding, ...],
        variable_lookup: MappingProxyType[str, RuntimeExecutionVariable],
        binding_lookup: MappingProxyType[str, RuntimeExecutionBinding],
        descriptor_lookup: MappingProxyType[str, RuntimeExecutionContextDescriptor],
        context_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionContextStatistics:
        
        variable_count = len(variables)
        binding_count = len(bindings)
        required_variable_count = sum(1 for v in variables if v.required)
        optional_variable_count = variable_count - required_variable_count
        
        return RuntimeExecutionContextStatistics(
            variable_count=variable_count,
            binding_count=binding_count,
            required_variable_count=required_variable_count,
            optional_variable_count=optional_variable_count,
            variable_lookup_count=len(variable_lookup),
            binding_lookup_count=len(binding_lookup),
            descriptor_lookup_count=len(descriptor_lookup),
            context_lookup_count=len(context_lookup)
        )
