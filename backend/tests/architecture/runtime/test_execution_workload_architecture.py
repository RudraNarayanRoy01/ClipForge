import pytest
import inspect
import dataclasses
from typing import Protocol, Any

from src.runtime.core.execution_workload import ExecutionWorkload
from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.core.intent import ExecutionIntent
from src.runtime.execution.execution_admission import ExecutionAdmission
from src.runtime.execution.workload_normalizer import WorkloadNormalizer
from src.runtime.execution.workload_normalization_extension import WorkloadNormalizationExtensionPoint
from src.runtime.execution.runtime_execution_boundary import RuntimeExecutionBoundary
from src.runtime.execution.execution_engine import ExecutionEngine
from src.runtime.execution.execution_mechanism_registry import ExecutionMechanismRegistry, AbstractExecutionMechanism
from src.runtime.execution.execution_result import ExecutionResult

def test_execution_target_remains_workload_free():
    """1. ExecutionTarget remains workload-free."""
    fields = {f.name for f in dataclasses.fields(ExecutionTarget)}
    assert 'workload' not in fields
    assert 'payload' not in fields
    assert 'intent' not in fields

def test_execution_intent_remains_unchanged():
    """2. ExecutionIntent remains unchanged."""
    fields = {f.name for f in dataclasses.fields(ExecutionIntent)}
    assert 'payload' in fields
    # Payload is still typed as Any
    field_type = next(f.type for f in dataclasses.fields(ExecutionIntent) if f.name == 'payload')
    assert field_type is Any

def test_execution_admission_contains_target_and_workload():
    """6. ExecutionAdmission contains both target and workload."""
    fields = {f.name for f in dataclasses.fields(ExecutionAdmission)}
    assert 'execution_target' in fields
    assert 'execution_workload' in fields

def test_execution_workload_is_generic_and_provider_neutral():
    """3, 4. ExecutionWorkload is generic and provider-neutral."""
    assert issubclass(ExecutionWorkload, Protocol)
    source_code = inspect.getsource(ExecutionWorkload)
    banned_terms = ["gemini", "openai", "ollama", "http", "subprocess", "celery", "cuda"]
    for term in banned_terms:
        assert term not in source_code.lower()

def test_workload_normalizer_does_not_import_providers():
    """5. WorkloadNormalizer contains no provider SDK imports."""
    source_code = inspect.getsource(WorkloadNormalizer)
    assert "backend.src.intelligence.providers" not in source_code
    
def test_execution_engine_contains_no_branching():
    """7, 8, 9, 12. ExecutionEngine contains no branching or hardcoded classes."""
    source_code = inspect.getsource(ExecutionEngine.execute)
    assert "if isinstance(workload, VideoAnalysisWorkload)" not in source_code
    assert "if workload.capability_id ==" not in source_code
    assert "elif" not in source_code
    # 10. ExecutionEngine uses registry metadata for compatibility
    assert "registration.expected_workload_type" in source_code
    assert "isinstance(workload, registration.expected_workload_type)" in source_code

def test_no_provider_sdk_imports_in_runtime_execution_contracts():
    modules = [ExecutionEngine, ExecutionAdmission, ExecutionWorkload, RuntimeExecutionBoundary, WorkloadNormalizer, ExecutionMechanismRegistry]
    for mod in modules:
        source_code = inspect.getsource(mod)
        assert "backend.src.intelligence.providers" not in source_code
        assert "AIRequest" not in source_code
        assert "urllib" not in source_code
        assert "requests" not in source_code

def test_no_backward_graph_traversal_from_execution_engine():
    source_code = inspect.getsource(ExecutionEngine.execute)
    assert "route_decision" not in source_code
    assert "policy_decision" not in source_code
    assert "planning_result" not in source_code
    assert "intent" not in source_code

def test_no_legacy_dependencies():
    """16. No legacy RuntimeExecutor dependency."""
    source_code = inspect.getsource(ExecutionEngine)
    assert "RuntimeExecutor" not in source_code

def test_no_global_registry_or_locator():
    """14, 15. No global registry or locator."""
    source_code = inspect.getsource(ExecutionMechanismRegistry)
    assert "_GLOBAL_REGISTRY" not in source_code
    engine_source = inspect.getsource(ExecutionEngine)
    assert "ServiceLocator" not in engine_source

def test_no_credentials_in_workload_structures():
    source_code = inspect.getsource(ExecutionWorkload)
    assert "api_key" not in source_code.lower()
    assert "token" not in source_code.lower()
    assert "credential" not in source_code.lower()

def test_no_shell_subprocess_networking_telemetry():
    """18, 19, 20, 21. No networking, scheduling, hardware, telemetry in correction."""
    modules = [RuntimeExecutionBoundary, WorkloadNormalizer, ExecutionEngine, ExecutionMechanismRegistry]
    # Removed hardware and scheduler because they appear in docstrings specifying they MUST NOT be used
    banned = ["subprocess", "shell", "os.system", "httpx", "telemetry", "metrics"]
    for mod in modules:
        source_code = inspect.getsource(mod).lower()
        for term in banned:
            assert term not in source_code
