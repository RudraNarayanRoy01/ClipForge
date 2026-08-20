import pytest
from unittest.mock import MagicMock
from typing import Optional, Any

from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.core.execution_workload import ExecutionWorkload
from src.runtime.execution.execution_admission import ExecutionAdmission
from src.runtime.execution.execution_result import ExecutionResult, ExecutionOutcome
from src.runtime.execution.execution_engine import ExecutionEngine, WorkloadCompatibilityError
from src.runtime.execution.execution_mechanism_registry import ExecutionMechanismRegistry, MechanismRegistration, AbstractExecutionMechanism, MechanismResolutionError

class DummyWorkload(ExecutionWorkload):
    @property
    def capability_id(self) -> str:
        return "dummy-cap"

class AnotherWorkload(ExecutionWorkload):
    @property
    def capability_id(self) -> str:
        return "another-cap"

class FakeSuccessMechanism(AbstractExecutionMechanism[DummyWorkload]):
    def __init__(self) -> None:
        self.received_target: Optional[ExecutionTarget] = None
        self.received_workload: Optional[Any] = None
        self.invoked = False

    def execute(self, target: ExecutionTarget, workload: DummyWorkload) -> tuple[ExecutionOutcome, Optional[str]]:
        self.received_target = target
        self.received_workload = workload
        self.invoked = True
        return ExecutionOutcome.SUCCESS, None

class FakeFailureMechanism(AbstractExecutionMechanism[DummyWorkload]):
    def __init__(self) -> None:
        self.received_target: Optional[ExecutionTarget] = None
        self.received_workload: Optional[Any] = None
        self.invoked = False

    def execute(self, target: ExecutionTarget, workload: DummyWorkload) -> tuple[ExecutionOutcome, Optional[str]]:
        self.received_target = target
        self.received_workload = workload
        self.invoked = True
        return ExecutionOutcome.FAILED, "external provider error"

class FakeExceptionMechanism(AbstractExecutionMechanism[DummyWorkload]):
    def execute(self, target: ExecutionTarget, workload: DummyWorkload) -> tuple[ExecutionOutcome, Optional[str]]:
        raise KeyError("unexpected programming defect")

def _create_target() -> ExecutionTarget:
    return ExecutionTarget(
        route_decision=MagicMock(),
        target_id="test_target_id",
        target_class="test_class",
        provider="test_provider"
    )

def _setup_registry(mechanism) -> ExecutionMechanismRegistry:
    registry = ExecutionMechanismRegistry()
    registry.register("test_provider", "dummy-cap", DummyWorkload, mechanism)
    return registry

def test_engine_construction():
    registry = ExecutionMechanismRegistry()
    engine = ExecutionEngine(mechanism_registry=registry)
    assert getattr(engine, "_mechanism_registry", None) is registry

def test_target_identity_end_to_end():
    target = _create_target()
    workload = DummyWorkload()
    admission = ExecutionAdmission(execution_target=target, execution_workload=workload)
    mechanism = FakeSuccessMechanism()
    registry = _setup_registry(mechanism)
    engine = ExecutionEngine(mechanism_registry=registry)

    result = engine.execute(admission)

    assert mechanism.invoked is True
    assert mechanism.received_target is target
    assert mechanism.received_workload is workload
    assert result.execution_target is target
    assert result.outcome == ExecutionOutcome.SUCCESS
    assert result.error_message is None

def test_failure_translation():
    target = _create_target()
    workload = DummyWorkload()
    admission = ExecutionAdmission(execution_target=target, execution_workload=workload)
    mechanism = FakeFailureMechanism()
    registry = _setup_registry(mechanism)
    engine = ExecutionEngine(mechanism_registry=registry)

    result = engine.execute(admission)

    assert result.execution_target is target
    assert result.outcome == ExecutionOutcome.FAILED
    assert result.error_message == "external provider error"

def test_unexpected_error_propagation():
    target = _create_target()
    workload = DummyWorkload()
    admission = ExecutionAdmission(execution_target=target, execution_workload=workload)
    mechanism = FakeExceptionMechanism()
    registry = _setup_registry(mechanism)
    engine = ExecutionEngine(mechanism_registry=registry)

    result = engine.execute(admission)

    assert result.execution_target is target
    assert result.outcome == ExecutionOutcome.FAILED
    assert "unexpected programming defect" in result.error_message
    assert "KeyError" in result.error_message

def test_admission_type_enforcement():
    registry = ExecutionMechanismRegistry()
    engine = ExecutionEngine(mechanism_registry=registry)

    with pytest.raises(TypeError, match="admission must be an instance of ExecutionAdmission"):
        engine.execute("fake_admission") # type: ignore

class HackedWorkload(ExecutionWorkload):
    @property
    def capability_id(self) -> str:
        return "dummy-cap"

def test_workload_compatibility_enforcement():
    target = _create_target()
    # Provide the WRONG workload type, but with the right capability_id to pass resolution
    workload = HackedWorkload()
    admission = ExecutionAdmission(execution_target=target, execution_workload=workload)
    mechanism = FakeSuccessMechanism()
    registry = _setup_registry(mechanism)
    engine = ExecutionEngine(mechanism_registry=registry)

    result = engine.execute(admission)
    assert result.execution_target is target
    assert result.outcome == ExecutionOutcome.REJECTED
    assert "is incompatible with expected type" in result.error_message

def test_mechanism_resolution_failure():
    target = _create_target()
    workload = DummyWorkload()
    admission = ExecutionAdmission(execution_target=target, execution_workload=workload)
    registry = ExecutionMechanismRegistry() # Empty registry
    engine = ExecutionEngine(mechanism_registry=registry)

    result = engine.execute(admission)

    assert result.execution_target is target
    assert result.outcome == ExecutionOutcome.REJECTED
    assert "No mechanism registered for provider" in result.error_message

def test_no_internal_registry_construction():
    with pytest.raises(TypeError):
        ExecutionEngine() # type: ignore
