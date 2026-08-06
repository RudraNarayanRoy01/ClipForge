from typing import Tuple, Any, Dict
from types import MappingProxyType
from .runtime_execution_plan_identity import RuntimeExecutionPlanIdentity
from .runtime_execution_plan_descriptor import RuntimeExecutionPlanDescriptor
from .runtime_execution_plan_metadata import RuntimeExecutionPlanMetadata
from .runtime_execution_layer import RuntimeExecutionLayer
from .runtime_execution_dependency_batch import RuntimeExecutionDependencyBatch
from .execution_plan_statistics_builder import ExecutionPlanStatisticsBuilder
from .execution_plan_snapshot_factory import ExecutionPlanSnapshotFactory
from .runtime_execution_plan_validator import RuntimeExecutionPlanValidator

class ExecutionPlanFactory:
    
    @classmethod
    def create_identity(cls,
                        descriptor: RuntimeExecutionPlanDescriptor,
                        metadata: RuntimeExecutionPlanMetadata,
                        layers: Tuple[RuntimeExecutionLayer, ...]) -> RuntimeExecutionPlanIdentity:
        
        # Build Statistics
        statistics = ExecutionPlanStatisticsBuilder.build(layers)
        
        # Build Lookups
        layer_lookup_dict: Dict[str, RuntimeExecutionLayer] = {}
        batch_lookup_dict: Dict[str, RuntimeExecutionDependencyBatch] = {}
        
        for layer in layers:
            layer_lookup_dict[layer.layer_identifier] = layer
            for batch in layer.batches:
                batch_lookup_dict[batch.batch_identifier] = batch
                
        layer_lookup = MappingProxyType(layer_lookup_dict)
        batch_lookup = MappingProxyType(batch_lookup_dict)
        
        descriptor_lookup = MappingProxyType({descriptor.plan_id: descriptor})
        
        # The plan_lookup will initially point to the descriptor as a placeholder 
        # until the wrapper is created, or it can point to None, or it can just be a placeholder map
        # However, to be strictly correct, we'll map plan_id to a minimal dict or the descriptor itself.
        # Since identity cannot reference the wrapper (circular), it references descriptor.
        plan_lookup = MappingProxyType({descriptor.plan_id: descriptor})
        
        # Build Snapshot
        snapshot = ExecutionPlanSnapshotFactory.create(
            descriptor=descriptor,
            layers=layers,
            layer_lookup=layer_lookup,
            batch_lookup=batch_lookup,
            plan_lookup=plan_lookup,
            metadata=metadata,
            statistics=statistics
        )
        
        identity = RuntimeExecutionPlanIdentity(
            descriptor=descriptor,
            metadata=metadata,
            statistics=statistics,
            snapshot=snapshot,
            layers=layers,
            layer_lookup=layer_lookup,
            batch_lookup=batch_lookup,
            descriptor_lookup=descriptor_lookup,
            plan_lookup=plan_lookup
        )
        
        RuntimeExecutionPlanValidator.validate(identity)
        
        return identity
