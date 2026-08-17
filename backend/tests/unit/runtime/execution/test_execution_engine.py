import pytest
from unittest.mock import MagicMock
from typing import Optional

from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.execution.execution_admission import ExecutionAdmission
from src.runtime.execution.execution_result import ExecutionResult
from src.runtime.execution.execution_engine import ExecutionEngine, AbstractExecutionMechanism

class FakeSuccessMechanism:
    def __init__(self) -> None:
        self.received_target: Optional[ExecutionTarget] = None
        self.invoked = False
    
    def execute_target(self, target: ExecutionTarget) -> tuple[bool, Optional[str]]:
        self.received_target = target
        self.invoked = True
        return True, None

class FakeFailureMechanism:
    def __init__(self) -> None:
        self.received_target: Optional[ExecutionTarget] = None
        self.invoked = False
    
    def execute_target(self, target: ExecutionTarget) -> tuple[bool, Optional[str]]:
        self.received_target = target
        self.invoked = True
        return False, "external provider error"

class FakeExceptionMechanism:
    def execute_target(self, target: ExecutionTarget) -> tuple[bool, Optional[str]]:
        raise KeyError("unexpected programming defect")

def _create_target() -> ExecutionTarget:
    return ExecutionTarget(
        route_decision=MagicMock(),
        target_id="test_target_id",
        target_class="test_class",
        provider="test_provider"
    )

def test_engine_construction():
    """A. ENGINE CONSTRUCTION & B. DEPENDENCY IDENTITY"""
    mechanism = FakeSuccessMechanism()
    engine = ExecutionEngine(execution_mechanism=mechanism)
    # The engine should retain the injected mechanism (dependency identity)
    assert getattr(engine, "_execution_mechanism", None) is mechanism

def test_target_identity_end_to_end():
    """
    C. ADMISSION TARGET EXTRACTION
    D. MECHANISM INVOCATION
    E. TARGET IDENTITY
    F. SUCCESS TRANSLATION
    H. RESULT TARGET IDENTITY
    K. NO TARGET RECONSTRUCTION
    """
    target = _create_target()
    admission = ExecutionAdmission(execution_target=target)
    mechanism = FakeSuccessMechanism()
    engine = ExecutionEngine(execution_mechanism=mechanism)
    
    result = engine.execute(admission)
    
    # Mechanism was invoked
    assert mechanism.invoked is True
    
    # Target identity preserved into mechanism
    assert mechanism.received_target is target
    
    # Target identity preserved in result
    assert result.execution_target is target
    
    # Success translated correctly from mechanism outcome
    assert result.is_success is True
    assert result.error_message is None

def test_failure_translation():
    """G. FAILURE TRANSLATION & H. RESULT TARGET IDENTITY"""
    target = _create_target()
    admission = ExecutionAdmission(execution_target=target)
    mechanism = FakeFailureMechanism()
    engine = ExecutionEngine(execution_mechanism=mechanism)
    
    result = engine.execute(admission)
    
    # Target identity preserved
    assert result.execution_target is target
    
    # Failure translated correctly
    assert result.is_success is False
    assert result.error_message == "external provider error"

def test_unexpected_error_propagation():
    """I. UNEXPECTED ERROR PROPAGATION"""
    target = _create_target()
    admission = ExecutionAdmission(execution_target=target)
    mechanism = FakeExceptionMechanism()
    engine = ExecutionEngine(execution_mechanism=mechanism)
    
    # Engine does not silently swallow unexpected programming defects
    with pytest.raises(KeyError, match="unexpected programming defect"):
        engine.execute(admission)

def test_admission_type_enforcement():
    """J. NO FAKE SUCCESS"""
    mechanism = FakeSuccessMechanism()
    engine = ExecutionEngine(execution_mechanism=mechanism)
    
    # Fake success: trying to execute something that is not an admission 
    # should fail. Only valid ExecutionAdmissions are accepted.
    with pytest.raises(TypeError, match="admission must be an instance of ExecutionAdmission"):
        engine.execute("fake_admission") # type: ignore

def test_no_internal_mechanism_construction():
    """L. NO INTERNAL MECHANISM CONSTRUCTION"""
    # Verifies the engine relies entirely on injection
    with pytest.raises(TypeError):
        # Missing required positional argument: 'execution_mechanism'
        ExecutionEngine() # type: ignore
