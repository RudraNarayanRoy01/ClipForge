import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.context import RuntimeContext
from src.runtime.core.runtime_monitoring import (
    RuntimeMonitoring,
    MonitoringResult,
    StageMonitoringResult,
    MonitoringStatus
)
from src.runtime.core.adaptive_runtime import (
    AdaptationDecision,
    StageAdaptationDecision,
    AdaptationStatus
)

def test_monitoring_status_lifecycle_values():
    """Verify MonitoringStatus represents only observation lifecycle."""
    assert hasattr(MonitoringStatus, 'OBSERVED')
    assert hasattr(MonitoringStatus, 'PARTIAL')
    assert hasattr(MonitoringStatus, 'FAILED')
    assert hasattr(MonitoringStatus, 'INVALID')

def test_stage_monitoring_result_is_immutable():
    """Verify StageMonitoringResult cannot be mutated."""
    result = StageMonitoringResult(
        stage_identifier="stage-1",
        stage_name="Transcribe",
        status=MonitoringStatus.OBSERVED
    )
    
    with pytest.raises(FrozenInstanceError):
        result.stage_name = "New Name" # type: ignore
        
    with pytest.raises(FrozenInstanceError):
        result.status = MonitoringStatus.FAILED # type: ignore

def test_monitoring_result_is_immutable():
    """Verify MonitoringResult cannot be mutated."""
    result = MonitoringResult(
        session_id="session-123",
        stage_monitoring_results=[],
        status=MonitoringStatus.OBSERVED
    )
    
    with pytest.raises(FrozenInstanceError):
        result.session_id = "session-456" # type: ignore
        
    with pytest.raises(FrozenInstanceError):
        result.status = MonitoringStatus.FAILED # type: ignore

def test_runtime_context_exposes_monitoring():
    """Verify RuntimeContext acts as the composition root for monitoring."""
    context = RuntimeContext()
    assert hasattr(context, 'runtime_monitoring')
    assert isinstance(context.runtime_monitoring, RuntimeMonitoring)

def test_runtime_monitoring_observes_adaptation():
    """Verify RuntimeMonitoring consumes AdaptationDecision and produces MonitoringResult."""
    # Arrange
    context = RuntimeContext()
    monitoring = context.runtime_monitoring
    
    stage_decision = StageAdaptationDecision(
        stage_identifier="stage-1",
        stage_name="Analyze",
        status=AdaptationStatus.ADAPT,
        rationale="Needs retry"
    )
    
    adaptation = AdaptationDecision(
        session_id="session-123",
        stage_decisions=[stage_decision],
        status=AdaptationStatus.ADAPT,
        rationale="Execution required adaptation"
    )
    
    # Act
    monitoring_result = monitoring.observe_adaptation(adaptation)
    
    # Assert
    assert isinstance(monitoring_result, MonitoringResult)
    assert monitoring_result.session_id == "session-123"
    assert monitoring_result.status == MonitoringStatus.OBSERVED
    assert len(monitoring_result.stage_monitoring_results) == 1
    
    stage_obs = monitoring_result.stage_monitoring_results[0]
    assert stage_obs.stage_identifier == "stage-1"
    assert stage_obs.stage_name == "Analyze"
    assert stage_obs.status == MonitoringStatus.OBSERVED
    
    # Verify strict boundary properties
    assert "telemetry" not in monitoring_result.observation_metadata
    assert "metrics" not in monitoring_result.observation_metadata
    assert "optimization" not in monitoring_result.observation_metadata
    
def test_runtime_monitoring_handles_invalid_adaptation():
    """Verify RuntimeMonitoring handles invalid or empty adaptation gracefully."""
    monitoring = RuntimeMonitoring()
    
    # None adaptation
    result = monitoring.observe_adaptation(None) # type: ignore
    assert result.status == MonitoringStatus.INVALID
    
    # Invalid session id
    invalid_adaptation = AdaptationDecision(session_id="invalid")
    result = monitoring.observe_adaptation(invalid_adaptation)
    assert result.status == MonitoringStatus.INVALID
