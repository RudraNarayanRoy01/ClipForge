import uuid
from datetime import datetime, timedelta
import pytest
from dataclasses import FrozenInstanceError

from src.application.rendering.models import RenderJobId
from src.application.rendering.telemetry import (
    RenderEventType,
    RenderExecutionEvent,
    RenderExecutionHistory,
    RenderExecutionMetrics
)


def test_render_execution_event_is_immutable():
    job_id = RenderJobId.generate()
    event = RenderExecutionEvent.create(
        job_id=job_id,
        event_type=RenderEventType.JOB_CREATED,
        message="Job created"
    )

    with pytest.raises(FrozenInstanceError):
        event.message = "Changed message"
        
    with pytest.raises(FrozenInstanceError):
        event.metadata = {}


def test_render_execution_history_is_immutable_and_copy_on_write():
    job_id = RenderJobId.generate()
    history = RenderExecutionHistory(job_id=job_id)
    
    event = RenderExecutionEvent.create(
        job_id=job_id,
        event_type=RenderEventType.JOB_CREATED,
        message="Created"
    )
    
    new_history = history.record_event(event)
    
    assert len(history.events) == 0
    assert len(new_history.events) == 1
    assert new_history.events[0] == event


def test_render_execution_history_enforces_chronological_consistency():
    job_id = RenderJobId.generate()
    base_time = datetime.utcnow()
    
    event1 = RenderExecutionEvent.create(
        job_id=job_id,
        event_type=RenderEventType.JOB_CREATED,
        message="Created",
        timestamp=base_time
    )
    
    event2 = RenderExecutionEvent.create(
        job_id=job_id,
        event_type=RenderEventType.STARTED,
        message="Started",
        timestamp=base_time - timedelta(seconds=1)  # Older timestamp
    )
    
    history = RenderExecutionHistory(job_id=job_id).record_event(event1)
    
    with pytest.raises(ValueError, match="Chronological inconsistency"):
        history.record_event(event2)


def test_render_execution_history_rejects_mismatched_job_id():
    job_id1 = RenderJobId.generate()
    job_id2 = RenderJobId.generate()
    
    history = RenderExecutionHistory(job_id=job_id1)
    event = RenderExecutionEvent.create(
        job_id=job_id2,
        event_type=RenderEventType.JOB_CREATED,
        message="Created"
    )
    
    with pytest.raises(ValueError, match="does not match history job_id"):
        history.record_event(event)


def test_metrics_derivation_from_history():
    job_id = RenderJobId.generate()
    base_time = datetime.utcnow()
    
    history = RenderExecutionHistory(job_id=job_id)
    
    # Simulate a full job lifecycle
    events = [
        RenderExecutionEvent.create(job_id, RenderEventType.JOB_CREATED, "Created", timestamp=base_time),
        RenderExecutionEvent.create(job_id, RenderEventType.STARTED, "Started", timestamp=base_time + timedelta(seconds=1)),
        RenderExecutionEvent.create(job_id, RenderEventType.PROGRESS_UPDATED, "Progress", timestamp=base_time + timedelta(seconds=2)),
        RenderExecutionEvent.create(job_id, RenderEventType.COMPLETED, "Done", timestamp=base_time + timedelta(seconds=5))
    ]
    
    for event in events:
        history = history.record_event(event)
        
    metrics = RenderExecutionMetrics.from_history(history)
    
    assert metrics.job_id == job_id
    assert metrics.created_at == base_time
    assert metrics.started_at == base_time + timedelta(seconds=1)
    assert metrics.completed_at == base_time + timedelta(seconds=5)
    assert metrics.outcome == "COMPLETED"
    assert metrics.duration_seconds == 4.0
    assert metrics.failure_reason is None


def test_metrics_derivation_with_failure():
    job_id = RenderJobId.generate()
    base_time = datetime.utcnow()
    
    history = RenderExecutionHistory(job_id=job_id)
    
    events = [
        RenderExecutionEvent.create(job_id, RenderEventType.JOB_CREATED, "Created", timestamp=base_time),
        RenderExecutionEvent.create(job_id, RenderEventType.STARTED, "Started", timestamp=base_time + timedelta(seconds=1)),
        RenderExecutionEvent.create(
            job_id, 
            RenderEventType.FAILED, 
            "Failed processing", 
            metadata={"reason": "Out of memory"},
            timestamp=base_time + timedelta(seconds=3)
        )
    ]
    
    for event in events:
        history = history.record_event(event)
        
    metrics = RenderExecutionMetrics.from_history(history)
    
    assert metrics.outcome == "FAILED"
    assert metrics.duration_seconds == 2.0
    assert metrics.failure_reason == "Out of memory"


def test_serialization():
    job_id = RenderJobId.generate()
    history = RenderExecutionHistory(job_id=job_id)
    
    event = RenderExecutionEvent.create(
        job_id=job_id,
        event_type=RenderEventType.STARTED,
        message="Started",
        metadata={"worker_id": "worker-1"}
    )
    
    history = history.record_event(event)
    
    serialized = history.to_dict()
    
    assert serialized["job_id"] == str(job_id)
    assert len(serialized["events"]) == 1
    
    evt_dict = serialized["events"][0]
    assert evt_dict["event_id"] == str(event.event_id)
    assert evt_dict["event_type"] == "STARTED"
    assert evt_dict["message"] == "Started"
    assert evt_dict["metadata"] == {"worker_id": "worker-1"}
    
    # Ensure isoformat is a string
    assert isinstance(evt_dict["timestamp"], str)
