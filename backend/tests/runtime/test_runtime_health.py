import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.context import RuntimeContext
from src.runtime.core.runtime_health import (
    RuntimeHealthStatus,
    StageRuntimeHealth,
    RuntimeHealthReport,
    RuntimeHealth
)
from src.runtime.core.runtime_metrics import (
    RuntimeMetricStatus,
    StageRuntimeMetrics,
    RuntimeMetricsSnapshot
)


def test_stage_runtime_health_is_immutable():
    """Verify StageRuntimeHealth is immutable."""
    stage_health = StageRuntimeHealth(
        stage_identifier="test_stage",
        stage_name="Test Stage",
        status=RuntimeHealthStatus.HEALTHY,
        evaluation_timestamp=1.0,
        evaluation_metadata={}
    )

    with pytest.raises(FrozenInstanceError):
        stage_health.status = RuntimeHealthStatus.CRITICAL


def test_runtime_health_report_is_immutable():
    """Verify RuntimeHealthReport is immutable."""
    report = RuntimeHealthReport(
        session_id="test_session",
        stage_health_collection=[],
        status=RuntimeHealthStatus.HEALTHY,
        health_classification="OPERATIONAL",
        evaluation_timestamp=1.0,
        evaluation_metadata={}
    )

    with pytest.raises(FrozenInstanceError):
        report.status = RuntimeHealthStatus.WARNING


def test_runtime_context_exposes_runtime_health():
    """Verify RuntimeContext exposes RuntimeHealth subsystem."""
    context = RuntimeContext()
    
    assert context.runtime_health is not None
    assert isinstance(context.runtime_health, RuntimeHealth)


def test_runtime_health_produces_health_report():
    """Verify RuntimeHealth consumes metrics snapshot and produces health report."""
    health_system = RuntimeHealth()
    
    stage_metric = StageRuntimeMetrics(
        stage_identifier="stage_1",
        stage_name="Extraction",
        status=RuntimeMetricStatus.CALCULATED,
        measurements={"cpu_usage": 45.0},
        calculation_timestamp=1.0
    )
    
    metrics_snapshot = RuntimeMetricsSnapshot(
        session_id="session_42",
        stage_metrics=[stage_metric],
        status=RuntimeMetricStatus.CALCULATED,
        measurements={"total_stages": 1.0},
        calculation_metadata={},
        calculation_timestamp=1.0
    )
    
    report = health_system.evaluate_health(metrics_snapshot, current_time=2.0)
    
    assert report is not None
    assert isinstance(report, RuntimeHealthReport)
    assert report.session_id == "session_42"
    assert report.status == RuntimeHealthStatus.HEALTHY
    assert len(report.stage_health_collection) == 1
    
    stage_health = report.stage_health_collection[0]
    assert stage_health.stage_identifier == "stage_1"
    assert stage_health.status == RuntimeHealthStatus.HEALTHY


def test_runtime_health_handles_invalid_metrics():
    """Verify RuntimeHealth handles missing or invalid metrics snapshot gracefully."""
    health_system = RuntimeHealth()
    
    invalid_metrics = RuntimeMetricsSnapshot(
        session_id="invalid",
        stage_metrics=[],
        status=RuntimeMetricStatus.INVALID,
        measurements={},
        calculation_metadata={},
        calculation_timestamp=1.0
    )
    
    report = health_system.evaluate_health(invalid_metrics, current_time=2.0)
    
    assert report.session_id == "invalid"
    assert report.status == RuntimeHealthStatus.UNKNOWN
    assert report.health_classification == "INVALID_METRICS"
    assert "error" in report.evaluation_metadata


def test_runtime_metrics_snapshot_remains_unchanged():
    """Verify RuntimeHealth does not modify the input metrics snapshot."""
    health_system = RuntimeHealth()
    
    stage_metric = StageRuntimeMetrics(
        stage_identifier="stage_1",
        stage_name="Extraction",
        status=RuntimeMetricStatus.CALCULATED,
        measurements={"cpu_usage": 45.0},
        calculation_timestamp=1.0
    )
    
    metrics_snapshot = RuntimeMetricsSnapshot(
        session_id="session_42",
        stage_metrics=[stage_metric],
        status=RuntimeMetricStatus.CALCULATED,
        measurements={"total_stages": 1.0},
        calculation_metadata={"original": True},
        calculation_timestamp=1.0
    )
    
    health_system.evaluate_health(metrics_snapshot, current_time=2.0)
    
    # Assert metrics snapshot was not modified
    assert metrics_snapshot.session_id == "session_42"
    assert len(metrics_snapshot.stage_metrics) == 1
    assert "original" in metrics_snapshot.calculation_metadata
    assert metrics_snapshot.status == RuntimeMetricStatus.CALCULATED
