import hashlib
from typing import Tuple, Any
from types import MappingProxyType
from .runtime_execution_context_snapshot import RuntimeExecutionContextSnapshot
from .runtime_execution_context_descriptor import RuntimeExecutionContextDescriptor
from .runtime_execution_variable import RuntimeExecutionVariable
from .runtime_execution_binding import RuntimeExecutionBinding
from .runtime_execution_context_metadata import RuntimeExecutionContextMetadata
from .runtime_execution_context_statistics import RuntimeExecutionContextStatistics

class ExecutionContextSnapshotFactory:
    """
    Constructs deterministic context snapshots structurally.
    
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
    def _hash_string(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def create(
        descriptor: RuntimeExecutionContextDescriptor,
        variables: Tuple[RuntimeExecutionVariable, ...],
        bindings: Tuple[RuntimeExecutionBinding, ...],
        variable_lookup: MappingProxyType[str, RuntimeExecutionVariable],
        binding_lookup: MappingProxyType[str, RuntimeExecutionBinding],
        descriptor_lookup: MappingProxyType[str, RuntimeExecutionContextDescriptor],
        context_lookup: MappingProxyType[str, Any],
        metadata: RuntimeExecutionContextMetadata,
        statistics: RuntimeExecutionContextStatistics
    ) -> RuntimeExecutionContextSnapshot:
        
        descriptor_str = f"{descriptor.execution_id}|{descriptor.runtime_id}|{descriptor.graph_id}|{descriptor.plan_id}|{descriptor.context_id}|{descriptor.version}|{descriptor.schema_version}"
        descriptor_hash = ExecutionContextSnapshotFactory._hash_string(descriptor_str)
        
        vars_str = "|".join(f"{v.identifier}:{v.name}:{v.variable_type}:{v.required}:{v.default_reference}:{v.description}" for v in sorted(variables, key=lambda x: x.identifier))
        variable_hash = ExecutionContextSnapshotFactory._hash_string(vars_str)
        
        bindings_str = "|".join(f"{b.identifier}:{b.source_identifier}:{b.target_identifier}:{b.binding_type}:{b.description}" for b in sorted(bindings, key=lambda x: x.identifier))
        binding_hash = ExecutionContextSnapshotFactory._hash_string(bindings_str)
        
        var_lookup_str = "|".join(f"{k}:{v.identifier}" for k, v in sorted(variable_lookup.items()))
        variable_lookup_hash = ExecutionContextSnapshotFactory._hash_string(var_lookup_str)

        binding_lookup_str = "|".join(f"{k}:{v.identifier}" for k, v in sorted(binding_lookup.items()))
        binding_lookup_hash = ExecutionContextSnapshotFactory._hash_string(binding_lookup_str)

        desc_lookup_str = "|".join(f"{k}:{v.context_id}" for k, v in sorted(descriptor_lookup.items()))
        descriptor_lookup_hash = ExecutionContextSnapshotFactory._hash_string(desc_lookup_str)

        ctx_lookup_str = "|".join(f"{k}:present" for k in sorted(context_lookup.keys()))
        context_lookup_hash = ExecutionContextSnapshotFactory._hash_string(ctx_lookup_str)
        
        labels_str = "|".join(f"{k}:{v}" for k, v in sorted(metadata.labels.items()))
        annotations_str = "|".join(f"{k}:{v}" for k, v in sorted(metadata.annotations.items()))
        tags_str = "|".join(sorted(metadata.tags))
        metadata_hash = ExecutionContextSnapshotFactory._hash_string(f"{labels_str}#{annotations_str}#{tags_str}")
        
        stats_str = f"{statistics.variable_count}|{statistics.binding_count}|{statistics.required_variable_count}|{statistics.optional_variable_count}|{statistics.variable_lookup_count}|{statistics.binding_lookup_count}|{statistics.descriptor_lookup_count}|{statistics.context_lookup_count}"
        statistics_hash = ExecutionContextSnapshotFactory._hash_string(stats_str)
        
        context_hash_components = [
            descriptor_hash,
            variable_hash,
            binding_hash,
            variable_lookup_hash,
            binding_lookup_hash,
            descriptor_lookup_hash,
            context_lookup_hash,
            metadata_hash,
            statistics_hash
        ]
        context_hash = ExecutionContextSnapshotFactory._hash_string("-".join(context_hash_components))
        
        return RuntimeExecutionContextSnapshot(
            descriptor_hash=descriptor_hash,
            variable_hash=variable_hash,
            binding_hash=binding_hash,
            variable_lookup_hash=variable_lookup_hash,
            binding_lookup_hash=binding_lookup_hash,
            descriptor_lookup_hash=descriptor_lookup_hash,
            context_lookup_hash=context_lookup_hash,
            metadata_hash=metadata_hash,
            statistics_hash=statistics_hash,
            context_hash=context_hash
        )
