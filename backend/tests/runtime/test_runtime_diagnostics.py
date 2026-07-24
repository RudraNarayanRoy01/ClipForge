import pytest
import time
from dataclasses import FrozenInstanceError

from src.runtime.core.context import RuntimeContext
from src.runtime.core.runtime_health import RuntimeHealthReport, StageRuntimeHealth, RuntimeHealthStatus
from src.runtime.core.runtime_diagnostics import (
    RuntimeDiagnostics, 
    RuntimeDiagnosticsReport, 
    StageRuntimeDiagnostic, 
    RuntimeDiagnosticStatus
)


def test_runtime_context_exposes_diagnostics():
    """Verify RuntimeContext owns and exposes RuntimeDiagnostics."""
    context = RuntimeContext()
    assert hasattr(context, 'runtime_diagnostics')
    assert isinstance(context.runtime_diagnostics, RuntimeDiagnostics)


def test_runtime_diagnostics_report_is_immutable():
    """Verify RuntimeDiagnosticsReport cannot be modified after creation."""
    report = RuntimeDiagnosticsReport(
        session_id="test_session",
        stage_diagnostics_collection=[],
        status=RuntimeDiagnosticStatus.NORMAL,
        findings=[],
        probable_causes=[],
        confidence_level=0.9,
        diagnostic_timestamp=time.time(),
        diagnostic_metadata={}
    )
    
    with pytest.raises(FrozenInstanceError):
        report.session_id = "new_session"
        
    with pytest.raises(FrozenInstanceError):
        report.status = RuntimeDiagnosticStatus.CRITICAL


def test_stage_runtime_diagnostic_is_immutable():
    """Verify StageRuntimeDiagnostic cannot be modified after creation."""
    diagnostic = StageRuntimeDiagnostic(
        stage_identifier="test_stage",
        stage_name="Test Stage",
        status=RuntimeDiagnosticStatus.NORMAL
    )
    
    with pytest.raises(FrozenInstanceError):
        diagnostic.stage_identifier = "new_stage"


def test_diagnose_health_produces_valid_report():
    """Verify RuntimeDiagnostics correctly consumes a health report and produces a diagnostic report."""
    diagnostics = RuntimeDiagnostics()
    current_time = time.time()
    
    stage_health = StageRuntimeHealth(
        stage_identifier="stage_1",
        stage_name="Analysis",
        status=RuntimeHealthStatus.DEGRADED,
        evaluation_timestamp=current_time
    )
    
    health_report = RuntimeHealthReport(
        session_id="session_123",
        stage_health_collection=[stage_health],
        status=RuntimeHealthStatus.DEGRADED,
        health_classification="DEGRADED",
        evaluation_timestamp=current_time
    )
    
    diagnostic_report = diagnostics.diagnose_health(health_report, current_time)
    
    assert isinstance(diagnostic_report, RuntimeDiagnosticsReport)
    assert diagnostic_report.session_id == "session_123"
    assert diagnostic_report.status == RuntimeDiagnosticStatus.WARNING
    assert len(diagnostic_report.stage_diagnostics_collection) == 1
    
    stage_diag = diagnostic_report.stage_diagnostics_collection[0]
    assert isinstance(stage_diag, StageRuntimeDiagnostic)
    assert stage_diag.stage_identifier == "stage_1"
    assert stage_diag.status == RuntimeDiagnosticStatus.WARNING


def test_diagnostics_preserves_architectural_boundaries():
    """Verify diagnostics handles invalid health reports without crashing or modifying state."""
    diagnostics = RuntimeDiagnostics()
    invalid_report = RuntimeHealthReport(
        session_id="invalid",
        stage_health_collection=[]
    )
    
    report = diagnostics.diagnose_health(invalid_report, time.time())
    
    assert report.session_id == "invalid"
    assert report.status == RuntimeDiagnosticStatus.UNKNOWN
    assert len(report.findings) > 0
    assert "Invalid" in report.findings[0]

