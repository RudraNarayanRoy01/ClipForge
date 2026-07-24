import pytest
import time
from dataclasses import FrozenInstanceError

from src.runtime.core.runtime_diagnostics import (
    RuntimeDiagnosticStatus, 
    StageRuntimeDiagnostic, 
    RuntimeDiagnosticsReport
)
from src.runtime.core.runtime_optimization import (
    OptimizationPriority,
    StageOptimizationDecision,
    OptimizationDecision,
    RuntimeOptimization
)
from src.runtime.core.context import RuntimeContext

def test_optimization_priority_exists():
    assert OptimizationPriority.NONE is not None
    assert OptimizationPriority.LOW is not None
    assert OptimizationPriority.MEDIUM is not None
    assert OptimizationPriority.HIGH is not None
    assert OptimizationPriority.CRITICAL is not None

def test_stage_optimization_decision_immutability():
    decision = StageOptimizationDecision(
        stage_identifier="stage-1",
        stage_name="Test Stage",
        priority=OptimizationPriority.MEDIUM
    )
    with pytest.raises(FrozenInstanceError):
        decision.priority = OptimizationPriority.HIGH # type: ignore

def test_optimization_decision_immutability():
    decision = OptimizationDecision(
        session_id="session-1"
    )
    with pytest.raises(FrozenInstanceError):
        decision.priority = OptimizationPriority.HIGH # type: ignore

def test_runtime_context_exposes_optimization():
    context = RuntimeContext()
    assert context.runtime_optimization is not None
    assert isinstance(context.runtime_optimization, RuntimeOptimization)

def test_runtime_optimization_consumes_diagnostics_produces_decision():
    opt = RuntimeOptimization()
    
    current_time = time.time()
    
    stage_diag = StageRuntimeDiagnostic(
        stage_identifier="stage-1",
        stage_name="Test Stage",
        status=RuntimeDiagnosticStatus.WARNING,
        finding="High latency",
        probable_cause="Provider sluggishness",
        confidence_level=0.9,
        diagnostic_timestamp=current_time
    )
    
    report = RuntimeDiagnosticsReport(
        session_id="sess-123",
        stage_diagnostics_collection=[stage_diag],
        status=RuntimeDiagnosticStatus.WARNING,
        findings=["High latency"],
        probable_causes=["Provider sluggishness"],
        confidence_level=0.85,
        diagnostic_timestamp=current_time
    )
    
    decision = opt.optimize(report, current_time)
    
    assert isinstance(decision, OptimizationDecision)
    assert decision.session_id == "sess-123"
    assert decision.priority == OptimizationPriority.MEDIUM
    assert len(decision.stage_optimization_collection) == 1
    
    stage_dec = decision.stage_optimization_collection[0]
    assert stage_dec.stage_identifier == "stage-1"
    assert stage_dec.priority == OptimizationPriority.MEDIUM
    assert "Performance" in stage_dec.optimization_classification

def test_runtime_optimization_handles_invalid_diagnostics():
    opt = RuntimeOptimization()
    
    report = RuntimeDiagnosticsReport(
        session_id="invalid"
    )
    
    decision = opt.optimize(report, time.time())
    
    assert decision.session_id == "invalid"
    assert decision.priority == OptimizationPriority.NONE
    assert "error" in decision.optimization_metadata

def test_runtime_optimization_handles_critical_diagnostics():
    opt = RuntimeOptimization()
    current_time = time.time()
    
    stage_diag = StageRuntimeDiagnostic(
        stage_identifier="stage-2",
        stage_name="Critical Stage",
        status=RuntimeDiagnosticStatus.CRITICAL,
        finding="Provider failure",
        probable_cause="Connection timeout"
    )
    
    report = RuntimeDiagnosticsReport(
        session_id="sess-456",
        stage_diagnostics_collection=[stage_diag],
        status=RuntimeDiagnosticStatus.CRITICAL
    )
    
    decision = opt.optimize(report, current_time)
    
    assert decision.priority == OptimizationPriority.CRITICAL
    assert len(decision.stage_optimization_collection) == 1
    assert decision.stage_optimization_collection[0].priority == OptimizationPriority.CRITICAL

def test_runtime_optimization_deterministic_provider_independent():
    # Verify that nothing in the reasoning depends on a specific provider or hardware.
    # The structure alone ensures this, but we explicitly test that generic reasoning applies.
    
    opt = RuntimeOptimization()
    current_time = time.time()
    report = RuntimeDiagnosticsReport(
        session_id="sess-789",
        stage_diagnostics_collection=[],
        status=RuntimeDiagnosticStatus.NORMAL
    )
    
    decision = opt.optimize(report, current_time)
    assert decision.priority == OptimizationPriority.NONE
    assert decision.optimization_classifications[0] == "No optimizations needed"
