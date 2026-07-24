import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.context import RuntimeContext
from src.runtime.core.runtime_metrics import (
    RuntimeMetrics,
    RuntimeMetricsSnapshot,
    StageRuntimeMetrics,
    RuntimeMetricStatus
)
from src.runtime.core.runtime_telemetry import (
    TelemetrySnapshot,
    StageTelemetrySnapshot,
    TelemetryStatus
)

def test_runtime_metrics_snapshot_immutability():
    """
    Validate that RuntimeMetricsSnapshot is strictly immutable.
    It MUST NOT be modified after creation.
    """
    snapshot = RuntimeMetricsSnapshot(
        session_id="test_session",
        stage_metrics=[],
        status=RuntimeMetricStatus.CALCULATED,
        measurements={"cpu_usage_avg": 45.2},
        calculation_metadata={},
        calculation_timestamp=123.45
    )

    with pytest.raises(FrozenInstanceError):
        snapshot.session_id = "new_session"
        
    with pytest.raises(FrozenInstanceError):
        snapshot.status = RuntimeMetricStatus.INVALID


def test_stage_runtime_metrics_immutability():
    """
    Validate that StageRuntimeMetrics is strictly immutable.
    """
    stage_metrics = StageRuntimeMetrics(
        stage_identifier="stage_1",
        stage_name="ReasoningStage",
        status=RuntimeMetricStatus.CALCULATED,
        measurements={"duration_ms": 150.0},
        calculation_timestamp=123.45
    )

    with pytest.raises(FrozenInstanceError):
        stage_metrics.stage_identifier = "stage_2"


def test_runtime_context_exposes_metrics():
    """
    Validate that RuntimeContext owns and exposes RuntimeMetrics.
    """
    context = RuntimeContext()
    
    assert hasattr(context, "runtime_metrics")
    assert isinstance(context.runtime_metrics, RuntimeMetrics)
    
    # Ensure it's identical on multiple calls
    assert context.runtime_metrics is context.runtime_metrics


def test_runtime_metrics_consumes_telemetry_snapshot():
    """
    Validate that RuntimeMetrics consumes TelemetrySnapshot and produces RuntimeMetricsSnapshot.
    TelemetrySnapshot remains unchanged (enforcing immutability).
    """
    telemetry_stage = StageTelemetrySnapshot(
        stage_identifier="stage_1",
        stage_name="ReasoningStage",
        status=TelemetryStatus.CAPTURED,
        signals={"cpu_load": 0.5, "memory_used": 1024},
        capture_timestamp=100.0
    )
    
    telemetry_snapshot = TelemetrySnapshot(
        session_id="session_123",
        stage_telemetry_snapshots=[telemetry_stage],
        status=TelemetryStatus.CAPTURED,
        signals={"overall_health_signal": True},
        capture_metadata={"captured_by": "RuntimeTelemetry"},
        capture_timestamp=101.0
    )

    metrics = RuntimeMetrics()
    metrics_snapshot = metrics.calculate_metrics(telemetry_snapshot, current_time=102.0)

    # Validate output
    assert isinstance(metrics_snapshot, RuntimeMetricsSnapshot)
    assert metrics_snapshot.session_id == "session_123"
    assert metrics_snapshot.status == RuntimeMetricStatus.CALCULATED
    assert len(metrics_snapshot.stage_metrics) == 1
    
    # Validate stage metric
    stage_metric = metrics_snapshot.stage_metrics[0]
    assert stage_metric.stage_identifier == "stage_1"
    assert stage_metric.stage_name == "ReasoningStage"
    assert stage_metric.measurements["processed_signals_count"] == 2.0
    
    # Validate TelemetrySnapshot remains unchanged
    assert telemetry_snapshot.status == TelemetryStatus.CAPTURED
    assert len(telemetry_snapshot.stage_telemetry_snapshots) == 1


def test_runtime_metric_status_lifecycle():
    """
    Validate the RuntimeMetricStatus lifecycle enumerations.
    """
    assert hasattr(RuntimeMetricStatus, "CALCULATED")
    assert hasattr(RuntimeMetricStatus, "PARTIAL")
    assert hasattr(RuntimeMetricStatus, "FAILED")
    assert hasattr(RuntimeMetricStatus, "INVALID")
    
    # Ensure no health or diagnostics statuses
    assert not hasattr(RuntimeMetricStatus, "HEALTHY")
    assert not hasattr(RuntimeMetricStatus, "OPTIMIZED")
    assert not hasattr(RuntimeMetricStatus, "DIAGNOSED")


def test_runtime_metrics_snapshot_contains_quantitative_measurements_only():
    """
    Validate structural rules:
    RuntimeMetricsSnapshot and StageRuntimeMetrics MUST NOT contain 
    health evaluation, diagnostics, optimization, or learning logic.
    """
    # They should only possess these exact fields
    snapshot_fields = RuntimeMetricsSnapshot.__dataclass_fields__.keys()
    assert "health_score" not in snapshot_fields
    assert "diagnostics" not in snapshot_fields
    assert "optimization_recommendation" not in snapshot_fields
    assert "learned_knowledge" not in snapshot_fields
    assert "measurements" in snapshot_fields
    
    stage_fields = StageRuntimeMetrics.__dataclass_fields__.keys()
    assert "health_status" not in stage_fields
    assert "root_cause" not in stage_fields
    assert "measurements" in stage_fields


def test_invalid_telemetry_handling():
    """
    Validate that an invalid TelemetrySnapshot results in an invalid RuntimeMetricsSnapshot.
    """
    metrics = RuntimeMetrics()
    invalid_telemetry = TelemetrySnapshot(
        session_id="invalid",
        status=TelemetryStatus.INVALID
    )
    
    metrics_snapshot = metrics.calculate_metrics(invalid_telemetry, current_time=100.0)
    
    assert metrics_snapshot.session_id == "invalid"
    assert metrics_snapshot.status == RuntimeMetricStatus.INVALID
