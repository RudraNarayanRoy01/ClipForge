from typing import Tuple, Set
from .runtime_execution_plan_identity import RuntimeExecutionPlanIdentity
from .runtime_execution_layer import RuntimeExecutionLayer
from .runtime_execution_dependency_batch import RuntimeExecutionDependencyBatch
from .runtime_execution_exceptions import ExecutionValidationException

class RuntimeExecutionPlanValidator:
    
    @classmethod
    def validate(cls, identity: RuntimeExecutionPlanIdentity) -> None:
        cls._validate_layers(identity.layers)
        cls._validate_lookups(identity)
        cls._validate_identifiers(identity)

    @classmethod
    def _validate_layers(cls, layers: Tuple[RuntimeExecutionLayer, ...]) -> None:
        layer_ids: Set[str] = set()
        batch_ids: Set[str] = set()
        
        for layer in layers:
            if layer.layer_identifier in layer_ids:
                raise ExecutionValidationException(f"Duplicate layer identifier: {layer.layer_identifier}")
            layer_ids.add(layer.layer_identifier)
            
            if not layer.batches:
                raise ExecutionValidationException(f"Empty layer detected: {layer.layer_identifier}")
                
            for batch in layer.batches:
                if batch.batch_identifier in batch_ids:
                    raise ExecutionValidationException(f"Duplicate batch identifier: {batch.batch_identifier}")
                batch_ids.add(batch.batch_identifier)
                
                if not batch.ordered_node_identifiers:
                    raise ExecutionValidationException(f"Empty batch detected: {batch.batch_identifier}")

    @classmethod
    def _validate_lookups(cls, identity: RuntimeExecutionPlanIdentity) -> None:
        # Validate layer_lookup consistency
        for layer in identity.layers:
            if layer.layer_identifier not in identity.layer_lookup:
                raise ExecutionValidationException(f"Layer {layer.layer_identifier} missing from layer_lookup")
            if identity.layer_lookup[layer.layer_identifier] is not layer:
                raise ExecutionValidationException(f"Layer {layer.layer_identifier} lookup mismatch")
                
        # Validate batch_lookup consistency
        for layer in identity.layers:
            for batch in layer.batches:
                if batch.batch_identifier not in identity.batch_lookup:
                    raise ExecutionValidationException(f"Batch {batch.batch_identifier} missing from batch_lookup")
                if identity.batch_lookup[batch.batch_identifier] is not batch:
                    raise ExecutionValidationException(f"Batch {batch.batch_identifier} lookup mismatch")

        # Validate descriptor lookup
        if identity.descriptor.plan_id not in identity.descriptor_lookup:
            raise ExecutionValidationException("Descriptor missing from descriptor_lookup")
            
        # Validate plan lookup
        if identity.descriptor.plan_id not in identity.plan_lookup:
            raise ExecutionValidationException("Plan missing from plan_lookup")

    @classmethod
    def _validate_identifiers(cls, identity: RuntimeExecutionPlanIdentity) -> None:
        if not identity.descriptor.plan_id:
            raise ExecutionValidationException("Invalid plan_id in descriptor")
