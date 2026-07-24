import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.context import RuntimeContext
from src.runtime.core.runtime_telemetry import (
    RuntimeTelemetry,
    TelemetrySnapshot,
    StageTelemetrySnapshot,
    TelemetryStatus
)
from src.runtime.core.runtime_monitoring import (
    MonitoringResult,
    StageMonitoringResult,
    MonitoringStatus
)


def test_telemetry_status_lifecycle_values():
    """Verify TelemetryStatus represents only telemetry capture lifecycle."""
    assert hasattr(TelemetryStatus, 'CAPTURED')
    assert hasattr(TelemetryStatus, 'PARTIAL')
    assert hasattr(TelemetryStatus, 'FAILED')
    assert hasattr(TelemetryStatus, 'INVALID')


def test_stage_telemetry_snapshot_is_immutable():
    """Verify StageTelemetrySnapshot cannot be mutated."""
    result = StageTelemetrySnapshot(
        stage_identifier="stage-1",
        stage_name="Transcribe",
        status=TelemetryStatus.CAPTURED,
        signals={"test": "signal"},
        capture_timestamp=123.45
    )
    
    with pytest.raises(FrozenInstanceError):
        result.stage_name = "New Name" # type: ignore
        
    with pytest.raises(FrozenInstanceError):
        result.status = TelemetryStatus.FAILED # type: ignore


def test_telemetry_snapshot_is_immutable():
    """Verify TelemetrySnapshot cannot be mutated."""
    result = TelemetrySnapshot(
        session_id="session-123",
        stage_telemetry_snapshots=[],
        status=TelemetryStatus.CAPTURED,
        signals={"test": "signal"},
        capture_metadata={"meta": "data"},
        capture_timestamp=123.45
    )
    
    with pytest.raises(FrozenInstanceError):
        result.session_id = "session-456" # type: ignore
        
    with pytest.raises(FrozenInstanceError):
        result.status = TelemetryStatus.FAILED # type: ignore


def test_runtime_context_exposes_telemetry():
    """Verify RuntimeContext acts as the composition root for telemetry."""
    context = RuntimeContext()
    assert hasattr(context, 'runtime_telemetry')
    assert isinstance(context.runtime_telemetry, RuntimeTelemetry)


def test_runtime_telemetry_consumes_monitoring():
    """Verify RuntimeTelemetry consumes MonitoringResult and produces TelemetrySnapshot."""
    # Arrange
    context = RuntimeContext()
    telemetry = context.runtime_telemetry
    
    stage_observation = StageMonitoringResult(
        stage_identifier="stage-1",
        stage_name="Analyze",
        status=MonitoringStatus.OBSERVED,
        observation_summary="Observation"
    )
    
    monitoring_result = MonitoringResult(
        session_id="session-123",
        stage_monitoring_results=[stage_observation],
        status=MonitoringStatus.OBSERVED,
        observation_summary="Observation summary"
    )
    
    # Act
    snapshot = telemetry.capture_signals(monitoring_result, current_time=999.99)
    
    # Assert
    assert isinstance(snapshot, TelemetrySnapshot)
    assert snapshot.session_id == "session-123"
    assert snapshot.status == TelemetryStatus.CAPTURED
    assert snapshot.capture_timestamp == 999.99
    assert len(snapshot.stage_telemetry_snapshots) == 1
    
    stage_snapshot = snapshot.stage_telemetry_snapshots[0]
    assert stage_snapshot.stage_identifier == "stage-1"
    assert stage_snapshot.stage_name == "Analyze"
    assert stage_snapshot.status == TelemetryStatus.CAPTURED
    assert stage_snapshot.capture_timestamp == 999.99
    
    # Verify strict boundary properties - signal capture only
    assert "metrics" not in snapshot.signals
    assert "health" not in snapshot.signals
    assert "diagnostics" not in snapshot.signals
    assert "optimization" not in snapshot.signals
    assert "learning" not in snapshot.signals


def test_runtime_telemetry_handles_invalid_monitoring():
    """Verify RuntimeTelemetry handles invalid or empty monitoring gracefully."""
    telemetry = RuntimeTelemetry()
    
    # None monitoring result
    result = telemetry.capture_signals(None, current_time=0.0) # type: ignore
    assert result.status == TelemetryStatus.INVALID
    assert result.session_id == "invalid"
    
    # Invalid session id
    invalid_monitoring = MonitoringResult(session_id="invalid")
    result = telemetry.capture_signals(invalid_monitoring, current_time=0.0)
    assert result.status == TelemetryStatus.INVALID
