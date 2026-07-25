import time
import uuid
from typing import List

from .learning_model import LearningResult
from .optimization_model import (
    OptimizationResult,
    OptimizationDecision,
    OptimizationCategory,
    OptimizationPriority,
    OptimizationSummary
)


class RuntimeOptimization:
    """
    The Runtime optimization engine.
    
    Defines "How Runtime derives optimization decisions."
    Performs exactly one responsibility: Consumes LearningResult -> Produces OptimizationResult.
    
    It must NEVER:
    - Execute work.
    - Schedule work.
    - Perform retries.
    - Recover execution.
    - Observe execution.
    - Learn Runtime patterns.
    - Apply optimizations.
    - Allocate resources.
    - Coordinate workflows.
    - Manage queues.
    - Generate recommendations.
    - Perform analytics.
    - Perform monitoring.
    - Predict future execution.
    - Modify RuntimeContext.
    """
    
    def optimize(self, learning_result: LearningResult) -> OptimizationResult:
        """
        Consume an immutable LearningResult and produce an immutable OptimizationResult.
        
        Derives intents representing optimization opportunities, but never commands 
        execution or applies the optimizations. Ends its responsibility immediately 
        after producing the result.
        """
        now = time.time()
        
        # 1. Generate optimization identity
        optimization_id = f"opt-{uuid.uuid4().hex[:8]}"
        
        # 2. Derive optimization decisions based on learned patterns (without executing/allocating)
        decisions: List[OptimizationDecision] = []
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        
        for pattern in learning_result.patterns:
            category = OptimizationCategory.UNKNOWN
            priority = OptimizationPriority.LOW
            
            # Map learning categories to optimization categories and priorities
            # All decisions must express intent ("Improve X", "Reduce Y") and NOT commands ("Set X to Y").
            if pattern.category.value == "RETRY":
                category = OptimizationCategory.RETRY
                if pattern.confidence.value in ("HIGH", "VERY_HIGH"):
                    priority = OptimizationPriority.HIGH
                    description = "Improve retry efficiency based on repeated failures."
                    expected_benefit = "Reduced execution latency and lower resource waste."
                else:
                    priority = OptimizationPriority.MEDIUM
                    description = "Monitor retry stability for potential jitter adjustments."
                    expected_benefit = "Enhanced execution stability."
            elif pattern.category.value == "RESOURCE":
                category = OptimizationCategory.RESOURCE
                if pattern.confidence.value in ("HIGH", "VERY_HIGH"):
                    priority = OptimizationPriority.CRITICAL
                    description = "Reduce resource pressure to prevent starvation."
                    expected_benefit = "Maintained throughput and avoided OOM faults."
                else:
                    priority = OptimizationPriority.MEDIUM
                    description = "Optimize resource footprint."
                    expected_benefit = "Improved general resource availability."
            elif pattern.category.value == "PERFORMANCE":
                category = OptimizationCategory.PERFORMANCE
                priority = OptimizationPriority.MEDIUM
                description = "Enhance execution throughput and latency characteristics."
                expected_benefit = "Faster turnaround for execution tasks."
            else:
                description = f"General optimization opportunity derived from pattern: {pattern.description}"
                expected_benefit = "Incremental system improvement."
                
            # Count priorities
            if priority == OptimizationPriority.CRITICAL:
                critical_count += 1
            elif priority == OptimizationPriority.HIGH:
                high_count += 1
            elif priority == OptimizationPriority.MEDIUM:
                medium_count += 1
            else:
                low_count += 1
                
            decision = OptimizationDecision(
                category=category,
                priority=priority,
                description=description,
                supporting_patterns=[pattern.description],
                expected_benefit=expected_benefit
            )
            decisions.append(decision)
            
        # 3. Create summary
        total_decisions = len(decisions)
        summary_text = (
            f"Optimization derived from learning {learning_result.learning_identity}. "
            f"Produced {total_decisions} optimization decision(s)."
        )
        
        summary = OptimizationSummary(
            summary=summary_text,
            decision_count=total_decisions,
            critical_count=critical_count,
            high_priority_count=high_count,
            medium_priority_count=medium_count,
            low_priority_count=low_count
        )
        
        # 4. Produce immutable canonical outcome
        return OptimizationResult(
            optimization_identity=optimization_id,
            learning_identity=learning_result.learning_identity,
            summary=summary,
            decisions=decisions,
            created_at=now
        )
