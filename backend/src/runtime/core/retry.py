import time
import uuid
from typing import Dict, Any, Optional

from .lifecycle_model import LifecycleResult, LifecycleState
from .retry_model import (
    RetryResult,
    RetryDecision,
    RetryReason,
    RetryPolicy,
    RetrySummary,
    RetryIdentity
)

class RuntimeRetry:
    """
    The Runtime retry evaluation engine.
    
    Defines "How retry decisions are evaluated."
    Performs exactly one responsibility: LifecycleResult -> RetryResult.
    
    It is NOT an executor, scheduler, lifecycle manager, recovery engine, 
    observation service, optimization engine, workflow engine, queue manager, 
    or resource manager.
    
    It strictly evaluates whether an execution should be attempted again.
    It does NOT execute retries, recover execution state, reconstruct execution 
    context, restart work, perform rollback, or perform compensation.
    """
    
    def evaluate(self, lifecycle_result: LifecycleResult, default_policy: Optional[RetryPolicy] = None) -> RetryResult:
        """
        Evaluate a LifecycleResult and produce an immutable RetryResult.
        
        This method evaluates the state of the lifecycle to determine if a 
        retry should be recommended. It produces an outcome without executing 
        any recovery logic.
        """
        # Determine the effective policy to evaluate against
        policy = default_policy or RetryPolicy(
            maximum_attempts=3,
            current_attempt=1,
            retry_strategy="EXPONENTIAL_BACKOFF",
            retry_window=3600.0
        )
        
        # Evaluate decision and reason
        decision, reason = self._evaluate_decision(lifecycle_result, policy)
        
        # Build Summary
        summary_text = (
            f"Retry evaluated for lifecycle {lifecycle_result.lifecycle_identity.lifecycle_id}. "
            f"Decision: {decision.value}"
        )
        
        remaining = max(0, policy.maximum_attempts - policy.current_attempt)
        if decision != RetryDecision.RETRY:
            remaining = 0
            
        summary = RetrySummary(
            summary=summary_text,
            reason=reason.value,
            remaining_attempts=remaining,
            warnings=[]
        )
        
        # Generate Identity
        now = time.time()
        retry_identity = RetryIdentity(
            retry_id=f"retry-{uuid.uuid4().hex[:8]}",
            created_at=now
        )
        
        # Produce immutable outcome
        return RetryResult(
            retry_identity=retry_identity,
            lifecycle_identity=lifecycle_result.lifecycle_identity,
            decision=decision,
            reason=reason,
            policy=policy,
            summary=summary,
            metadata={}
        )
        
    def _evaluate_decision(self, lifecycle_result: LifecycleResult, policy: RetryPolicy) -> tuple[RetryDecision, RetryReason]:
        """
        Evaluate the raw decision based on lifecycle state and policy limits.
        """
        if lifecycle_result.state == LifecycleState.COMPLETED:
            return RetryDecision.DO_NOT_RETRY, RetryReason.SUCCESS_NO_RETRY
            
        if lifecycle_result.state == LifecycleState.TERMINATED:
            return RetryDecision.DO_NOT_RETRY, RetryReason.UNKNOWN
            
        if lifecycle_result.state == LifecycleState.FAILED:
            if policy.current_attempt >= policy.maximum_attempts:
                return RetryDecision.ABORT, RetryReason.POLICY_LIMIT
            
            # In a real implementation, we would inspect the ExecutionResult 
            # (or LifecycleResult metadata) to determine if it's transient vs model failure.
            # For now, default to TRANSIENT_FAILURE if policy allows retry.
            return RetryDecision.RETRY, RetryReason.TRANSIENT_FAILURE
            
        # Default fallback
        return RetryDecision.MANUAL_REVIEW, RetryReason.UNKNOWN
