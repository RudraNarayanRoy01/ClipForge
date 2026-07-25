import time
import uuid
from typing import Dict, Any, Optional

from .execution_model import ExecutionRequest
from .scheduling_model import (
    SchedulingIdentity,
    SchedulingDecision,
    SchedulingStatus,
    SchedulingPolicy,
    SchedulingStrategy,
    SchedulingPriority,
    QueueClassification
)


class RuntimeScheduler:
    """
    The canonical architectural scheduling engine for the Runtime.
    
    This subsystem determines *whether*, *when*, *how*, and in *which logical queue* 
    approved work should execute.
    
    It explicitly performs **Operational Decision Making** only.
    
    It MUST NOT:
    - Execute work (Not an execution engine)
    - Manage queues (Not a queue manager)
    - Retry work (Not a retry coordinator)
    - Manage lifecycle (Not a lifecycle manager)
    - Define policy (Not a policy engine)
    
    The evaluation flow is strictly:
    ExecutionRequest 
      -> Read Scheduling Policy 
      -> Read Scheduling Strategy 
      -> Evaluate Scheduling Decision 
      -> Produce immutable SchedulingDecision
      
    No mutation occurs.
    """
    def __init__(self) -> None:
        pass

    def schedule(
        self, 
        request: ExecutionRequest,
        policy: SchedulingPolicy = SchedulingPolicy.IMMEDIATE,
        strategy: SchedulingStrategy = SchedulingStrategy.FIFO,
        priority: SchedulingPriority = SchedulingPriority.NORMAL,
        queue_classification: QueueClassification = QueueClassification.BACKGROUND
    ) -> SchedulingDecision:
        """
        Evaluate an ExecutionRequest and produce a SchedulingDecision.
        
        The provided arguments (policy, strategy, priority, queue_classification)
        represent architectural assumptions or inputs supplied by the Runtime Policy layer.
        The Scheduler consumes these inputs but does NOT own permanent defaults.
        """
        
        # 1. Evaluate Scheduling Identity
        schedule_id = f"sch_{uuid.uuid4().hex}"
        current_time = time.time()
        
        identity = SchedulingIdentity(
            schedule_id=schedule_id,
            created_at=current_time,
            execution_identity=request.identity
        )
        
        # 2. Evaluate Scheduling Status based on policy and constraints
        # In a fully fleshed out system, this would evaluate actual readiness.
        # For this architectural boundary, we assume it's READY.
        status = SchedulingStatus.READY
        
        if policy == SchedulingPolicy.DEFERRED:
            status = SchedulingStatus.DEFERRED
            
        reasoning = (
            f"Evaluated ExecutionRequest {request.identity.execution_id}. "
            f"Policy: {policy.name}. Strategy: {strategy.name}."
        )

        # 3. Produce Immutable SchedulingDecision
        return SchedulingDecision(
            identity=identity,
            execution_identity=request.identity,
            status=status,
            priority=priority,
            policy=policy,
            strategy=strategy,
            queue_classification=queue_classification,
            scheduling_timestamp=current_time,
            scheduling_reasoning=reasoning,
            metadata={
                "source_request_id": request.identity.execution_id
            }
        )
