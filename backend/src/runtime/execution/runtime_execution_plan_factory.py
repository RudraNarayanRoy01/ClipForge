from typing import Tuple, Dict, Any
from .runtime_execution_plan_descriptor import RuntimeExecutionPlanDescriptor
from .runtime_execution_plan_metadata import RuntimeExecutionPlanMetadata
from .runtime_execution_layer import RuntimeExecutionLayer
from .execution_plan_factory import ExecutionPlanFactory
from .runtime_execution_plan import RuntimeExecutionPlan

class RuntimeExecutionPlanFactory:
    
    @classmethod
    def create(cls,
               descriptor: RuntimeExecutionPlanDescriptor,
               metadata: RuntimeExecutionPlanMetadata,
               layers: Tuple[RuntimeExecutionLayer, ...]) -> RuntimeExecutionPlan:
        
        identity = ExecutionPlanFactory.create_identity(
            descriptor=descriptor,
            metadata=metadata,
            layers=layers
        )
        
        return RuntimeExecutionPlan(
            identifier=descriptor.plan_id,
            identity=identity
        )
