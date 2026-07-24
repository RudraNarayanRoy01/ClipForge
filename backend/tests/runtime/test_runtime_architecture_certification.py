import pytest
import inspect
import dataclasses
from pathlib import Path

from src.runtime.core.execution_engine import ExecutionResult
from src.runtime.core.adaptive_runtime import AdaptationDecision
from src.runtime.core.runtime_monitoring import MonitoringResult, RuntimeMonitoring
from src.runtime.core.runtime_telemetry import TelemetrySnapshot, RuntimeTelemetry
from src.runtime.core.runtime_metrics import RuntimeMetricsSnapshot, RuntimeMetrics
from src.runtime.core.runtime_health import RuntimeHealthReport, RuntimeHealth
from src.runtime.core.runtime_diagnostics import RuntimeDiagnosticsReport, RuntimeDiagnostics
from src.runtime.core.runtime_optimization import OptimizationDecision, RuntimeOptimization
from src.runtime.core.runtime_learning import RuntimeKnowledge, RuntimeLearning
from src.runtime.core.context import RuntimeContext

def test_observation_reasoning_artifacts_are_immutable():
    """Verify that all artifacts in the observation and reasoning pipeline are immutable."""
    artifacts = [
        ExecutionResult,
        AdaptationDecision,
        MonitoringResult,
        TelemetrySnapshot,
        RuntimeMetricsSnapshot,
        RuntimeHealthReport,
        RuntimeDiagnosticsReport,
        OptimizationDecision,
        RuntimeKnowledge
    ]
    
    for artifact_cls in artifacts:
        assert dataclasses.is_dataclass(artifact_cls), f"{artifact_cls.__name__} must be a dataclass."
        assert artifact_cls.__dataclass_params__.frozen is True, f"{artifact_cls.__name__} must be frozen (immutable)."

def test_runtime_context_ownership_and_composition():
    """Verify RuntimeContext is the sole composition root and owns the subsystems."""
    context = RuntimeContext()
    
    assert isinstance(context.runtime_monitoring, RuntimeMonitoring)
    assert isinstance(context.runtime_telemetry, RuntimeTelemetry)
    assert isinstance(context.runtime_metrics, RuntimeMetrics)
    assert isinstance(context.runtime_health, RuntimeHealth)
    assert isinstance(context.runtime_diagnostics, RuntimeDiagnostics)
    assert isinstance(context.runtime_optimization, RuntimeOptimization)
    assert isinstance(context.runtime_learning, RuntimeLearning)
    
    # Subsystems should not be instantiating each other. 
    # Checking for hidden constructor arguments or instantiation.
    for subsystem in [RuntimeMonitoring, RuntimeTelemetry, RuntimeMetrics, RuntimeHealth, RuntimeDiagnostics, RuntimeOptimization, RuntimeLearning]:
        sig = inspect.signature(subsystem.__init__)
        assert len(sig.parameters) == 1, f"{subsystem.__name__} should not take dependencies in constructor."

def test_one_component_one_artifact_mapping():
    """Verify one component maps strictly to its one primary artifact return type."""
    monitoring_sig = inspect.signature(RuntimeMonitoring.observe_adaptation)
    assert monitoring_sig.return_annotation == MonitoringResult
    assert monitoring_sig.parameters['adaptation_decision'].annotation == AdaptationDecision

    telemetry_sig = inspect.signature(RuntimeTelemetry.capture_signals)
    assert telemetry_sig.return_annotation == TelemetrySnapshot
    assert telemetry_sig.parameters['monitoring_result'].annotation == MonitoringResult

    metrics_sig = inspect.signature(RuntimeMetrics.calculate_metrics)
    assert metrics_sig.return_annotation == RuntimeMetricsSnapshot
    assert metrics_sig.parameters['telemetry_snapshot'].annotation == TelemetrySnapshot

    health_sig = inspect.signature(RuntimeHealth.evaluate_health)
    assert health_sig.return_annotation == RuntimeHealthReport
    assert health_sig.parameters['metrics_snapshot'].annotation == RuntimeMetricsSnapshot

    diagnostics_sig = inspect.signature(RuntimeDiagnostics.diagnose_health)
    assert diagnostics_sig.return_annotation == RuntimeDiagnosticsReport
    assert diagnostics_sig.parameters['health_report'].annotation == RuntimeHealthReport

    optimization_sig = inspect.signature(RuntimeOptimization.optimize)
    assert optimization_sig.return_annotation == OptimizationDecision
    assert optimization_sig.parameters['diagnostics_report'].annotation == RuntimeDiagnosticsReport

    learning_sig = inspect.signature(RuntimeLearning.learn)
    assert learning_sig.return_annotation == RuntimeKnowledge
    assert learning_sig.parameters['optimization_decision'].annotation == OptimizationDecision

def test_dependency_direction():
    """
    Verify dependency direction by checking the annotations.
    Learning should not accept Optimization as a return value, etc.
    This is implicitly verified by `test_one_component_one_artifact_mapping`, 
    but we can explicitly check that no reverse imports exist.
    """
    learning_mod = inspect.getmodule(RuntimeLearning)
    # Learning should not import anything that depends on Learning
    assert 'OptimizationDecision' in dir(learning_mod), "Learning depends on OptimizationDecision"
    
    optimization_mod = inspect.getmodule(RuntimeOptimization)
    assert 'RuntimeLearning' not in dir(optimization_mod), "Optimization must not depend on Learning"
    
    diagnostics_mod = inspect.getmodule(RuntimeDiagnostics)
    assert 'RuntimeOptimization' not in dir(diagnostics_mod), "Diagnostics must not depend on Optimization"

def test_provider_and_hardware_independence():
    """
    Verify the Observation & Reasoning subsystems contain no provider 
    or hardware specific terminology.
    """
    banned_terms = [
        "Gemini", "OpenAI", "Ollama", "llama.cpp", "Claude",
        "CPU", "GPU", "CUDA", "ROCm", "Metal", "VRAM"
    ]
    
    subsystems = [
        RuntimeMonitoring, RuntimeTelemetry, RuntimeMetrics, 
        RuntimeHealth, RuntimeDiagnostics, RuntimeOptimization, RuntimeLearning
    ]
    
    for subsystem in subsystems:
        source_code = inspect.getsource(subsystem)
        for term in banned_terms:
            assert term not in source_code, f"Banned architectural term '{term}' found in {subsystem.__name__}."
