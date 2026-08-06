from typing import Tuple, Dict, Set, Any
from types import MappingProxyType
from .runtime_execution_variable import RuntimeExecutionVariable
from .runtime_execution_binding import RuntimeExecutionBinding
from .runtime_execution_context_descriptor import RuntimeExecutionContextDescriptor
from .runtime_execution_context_identity import RuntimeExecutionContextIdentity
from .execution_context_metadata_factory import ExecutionContextMetadataFactory
from .execution_context_statistics_builder import ExecutionContextStatisticsBuilder
from .execution_context_snapshot_factory import ExecutionContextSnapshotFactory
from .runtime_execution_context_validator import RuntimeExecutionContextValidator

class ExecutionContextFactory:
    """
    Constructs the Execution Context Identity structurally.
    
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
    def create(
        descriptor: RuntimeExecutionContextDescriptor,
        variables: Tuple[RuntimeExecutionVariable, ...],
        bindings: Tuple[RuntimeExecutionBinding, ...],
        labels: Dict[str, str],
        annotations: Dict[str, str],
        tags: Set[str]
    ) -> RuntimeExecutionContextIdentity:
        
        RuntimeExecutionContextValidator.validate_context_state(descriptor, variables, bindings)
        
        metadata = ExecutionContextMetadataFactory.create(labels, annotations, tags)
        
        variable_lookup_dict = {var.identifier: var for var in variables}
        binding_lookup_dict = {binding.identifier: binding for binding in bindings}
        
        variable_lookup = MappingProxyType(variable_lookup_dict)
        binding_lookup = MappingProxyType(binding_lookup_dict)
        descriptor_lookup = MappingProxyType({descriptor.context_id: descriptor})
        context_lookup = MappingProxyType({})
        
        statistics = ExecutionContextStatisticsBuilder.build(
            variables=variables,
            bindings=bindings,
            variable_lookup=variable_lookup,
            binding_lookup=binding_lookup,
            descriptor_lookup=descriptor_lookup,
            context_lookup=context_lookup
        )
        
        snapshot = ExecutionContextSnapshotFactory.create(
            descriptor=descriptor,
            variables=variables,
            bindings=bindings,
            variable_lookup=variable_lookup,
            binding_lookup=binding_lookup,
            descriptor_lookup=descriptor_lookup,
            context_lookup=context_lookup,
            metadata=metadata,
            statistics=statistics
        )
        
        return RuntimeExecutionContextIdentity(
            descriptor=descriptor,
            metadata=metadata,
            variables=variables,
            bindings=bindings,
            statistics=statistics,
            snapshot=snapshot,
            variable_lookup=variable_lookup,
            binding_lookup=binding_lookup,
            descriptor_lookup=descriptor_lookup,
            context_lookup=context_lookup
        )
