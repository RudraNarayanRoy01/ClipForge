import time
import uuid
from typing import List, Dict, Any, Optional

from .retry_model import RetryResult
from .observation_model import (
    ObservationResult,
    ObservationIdentity,
    ObservationSummary,
    ObservationRecord,
    ObservationCategory,
    ObservationSeverity
)

class RuntimeObservation:
    """
    The Runtime observation engine.
    
    Defines "How Runtime observations are extracted."
    Performs exactly one responsibility: RetryResult -> ObservationResult.
    
    It is NOT an executor, scheduler, lifecycle manager, retry engine, 
    monitoring engine, analytics engine, learning engine, optimization engine, 
    recommendation engine, workflow engine, queue manager, or resource manager.
    
    It does NOT continuously monitor Runtime, collect telemetry, collect metrics,
    stream events, publish logs, or integrate with Prometheus/Datadog/OpenTelemetry.
    """
    
    def extract_observations(self, retry_result: RetryResult) -> ObservationResult:
        """
        Consume a RetryResult and produce an immutable ObservationResult.
        """
        now = time.time()
        
        # 1. Generate identity
        observation_identity = ObservationIdentity(
            observation_id=f"obs-{uuid.uuid4().hex[:8]}",
            created_at=now
        )
        
        # 2. Extract records (purely descriptive)
        records: List[ObservationRecord] = []
        warning_count = 0
        error_count = 0
        critical_count = 0
        
        # We classify based on retry_result's reason and decision
        # Note: We do NOT interpret or assign scores. We simply record what we see.
        decision_val = retry_result.decision.value
        reason_val = retry_result.reason.value
        
        category = ObservationCategory.RETRY
        severity = ObservationSeverity.INFO
        
        if decision_val in ["RETRY", "MANUAL_REVIEW"]:
            severity = ObservationSeverity.WARNING
            warning_count += 1
        elif decision_val == "ABORT":
            severity = ObservationSeverity.ERROR
            error_count += 1
            
        record = ObservationRecord(
            category=category,
            severity=severity,
            message=f"Retry decision resulted in {decision_val} due to {reason_val}",
            timestamp=now,
            context={"decision": decision_val, "reason": reason_val}
        )
        records.append(record)
        
        # 3. Create summary
        total_observations = len(records)
        summary_text = (
            f"Observation extracted for retry {retry_result.retry_identity.retry_id}. "
            f"Recorded {total_observations} observation(s)."
        )
        
        summary = ObservationSummary(
            summary=summary_text,
            observation_count=total_observations,
            warning_count=warning_count,
            error_count=error_count,
            critical_count=critical_count
        )
        
        # 4. Produce immutable outcome
        return ObservationResult(
            observation_identity=observation_identity,
            retry_identity=retry_result.retry_identity,
            summary=summary,
            records=records,
            created_at=now
        )
