from typing import Tuple
from .runtime_execution_plan_statistics import RuntimeExecutionPlanStatistics
from .runtime_execution_layer import RuntimeExecutionLayer

class ExecutionPlanStatisticsBuilder:
    
    @classmethod
    def build(cls, layers: Tuple[RuntimeExecutionLayer, ...]) -> RuntimeExecutionPlanStatistics:
        layer_count = len(layers)
        dependency_batch_count = sum(len(layer.batches) for layer in layers)
        
        planned_step_count = sum(
            len(batch.ordered_node_identifiers) 
            for layer in layers 
            for batch in layer.batches
        )
        
        graph_depth = layer_count
        
        maximum_parallel_groups = max(
            (len(layer.batches) for layer in layers), 
            default=0
        )
        
        node_count = planned_step_count
        
        return RuntimeExecutionPlanStatistics(
            layer_count=layer_count,
            dependency_batch_count=dependency_batch_count,
            planned_step_count=planned_step_count,
            graph_depth=graph_depth,
            maximum_parallel_groups=maximum_parallel_groups,
            node_count=node_count
        )
