import pytest
import inspect
import dataclasses
from datetime import datetime
from types import MappingProxyType

from src.runtime.core.provider_health_manager import ProviderHealthManager
from src.runtime.core.provider_failover_manager import ProviderFailoverManager
from src.runtime.core.runtime_retry_manager import RuntimeRetryManager
from src.runtime.core.runtime_scheduling_manager import RuntimeSchedulingManager
from src.runtime.core.runtime_execution_manager import RuntimeExecutionManager

from src.runtime.domain.runtime_execution_model import (
    RuntimeExecutionStatus,
    RuntimeExecutionTrigger,
    RuntimeExecutionPreparationResult
)
from src.runtime.execution.runtime_execution_outcome import RuntimeExecutionOutcome
from src.runtime.execution.runtime_execution_result import RuntimeExecutionResult
from src.runtime.execution.runtime_execution_terminal_consistency_validator import RuntimeExecutionTerminalConsistencyValidator
from src.runtime.execution.runtime_execution_lifecycle_state import RuntimeExecutionLifecycleState

from src.runtime.execution.runtime_execution_identity import RuntimeExecutionIdentity
from src.runtime.execution.runtime_execution_descriptor import RuntimeExecutionDescriptor
from src.runtime.execution.runtime_execution_metadata import RuntimeExecutionMetadata
from src.runtime.execution.runtime_execution_snapshot import RuntimeExecutionSnapshot


@pytest.fixture
def execution_environment():
    """
    Establish the legitimate public dependency chain.
    No private internals or mocks are required.
    """
    health = ProviderHealthManager()
    failover = ProviderFailoverManager(health)
    retry = RuntimeRetryManager(failover)
    sched = RuntimeSchedulingManager(retry)
    manager = RuntimeExecutionManager(sched)
    
    return manager, health, failover, retry, sched


def _register_chain(manager, health, failover, retry, sched, provider_id: str):
    """Local helper to register provider across the chain."""
    health.register_provider(provider_id)
    failover.register_provider(provider_id)
    retry.register_provider(provider_id)
    sched.register_provider(provider_id)
    manager.register_provider(provider_id)


def test_real_structural_abort_reset(execution_environment):
    """
    SCENARIO 1 — REAL STRUCTURAL ABORT / RESET
    """
    provider_id = "test_provider_1"
    manager, health, failover, retry, sched = execution_environment
    
    # 1. Register through the legitimate chain
    _register_chain(manager, health, failover, retry, sched, provider_id)
    
    # Verify registration establishes ABORTED/UNKNOWN initially
    info = manager.get_execution(provider_id)
    assert info.current_status == RuntimeExecutionStatus.ABORTED
    assert info.trigger == RuntimeExecutionTrigger.UNKNOWN
    
    # 2. Elevate to PREPARED state (simulate preparation)
    manager.record_execution(
        provider_id, 
        RuntimeExecutionTrigger.MANUAL_EXECUTION
    )
    
    # Verify the pre-reset state
    info_pre_reset = manager.get_execution(provider_id)
    assert info_pre_reset.current_status == RuntimeExecutionStatus.PREPARED
    assert info_pre_reset.trigger == RuntimeExecutionTrigger.MANUAL_EXECUTION
    
    # 3. Call actual clear_execution
    result = manager.clear_execution(provider_id)
    
    # 4. Verify return type
    assert isinstance(result, RuntimeExecutionPreparationResult)
    
    # 5. Verify current_status == ABORTED
    assert result.execution_info.current_status == RuntimeExecutionStatus.ABORTED
    
    # 6. Verify trigger == UNKNOWN
    assert result.execution_info.trigger == RuntimeExecutionTrigger.UNKNOWN
    
    # 7. Verify no RuntimeExecutionResult is produced (structurally checked by return type)
    assert not isinstance(result, RuntimeExecutionResult)


def test_aborted_has_no_certified_result_mapping():
    """
    SCENARIO 2 — ABORTED HAS NO CERTIFIED RESULT MAPPING
    """
    validator = RuntimeExecutionTerminalConsistencyValidator()
    
    # Setup a dummy identity for results
    identity = RuntimeExecutionIdentity(
        descriptor=RuntimeExecutionDescriptor("exec_1", "rt_1", "boot_1", "1.0", "1.0"),
        metadata=RuntimeExecutionMetadata("test", "test", datetime.utcnow(), datetime.utcnow(), frozenset(), MappingProxyType({}), "1.0"),
        status=RuntimeExecutionStatus.ABORTED,
        snapshot=RuntimeExecutionSnapshot("1", "2", "3", "4", "5", "6")
    )
    
    aborted_state = RuntimeExecutionLifecycleState(current_status=RuntimeExecutionStatus.ABORTED)
    
    success_result = RuntimeExecutionResult(
        identity=identity,
        outcome=RuntimeExecutionOutcome.SUCCESS,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        duration_seconds=1.0
    )
    
    failed_result = RuntimeExecutionResult(
        identity=identity,
        outcome=RuntimeExecutionOutcome.FAILED,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        duration_seconds=1.0,
        failure_reason="test"
    )
    
    cancelled_result = RuntimeExecutionResult(
        identity=identity,
        outcome=RuntimeExecutionOutcome.CANCELLED,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        duration_seconds=1.0
    )
    
    # Verify ONLY the ABORTED boundary as required
    assert validator.is_consistent(aborted_state, success_result) is False
    assert validator.is_consistent(aborted_state, failed_result) is False
    assert validator.is_consistent(aborted_state, cancelled_result) is False


def test_structural_reset_is_not_execution_cancellation(execution_environment):
    """
    SCENARIO 3 — STRUCTURAL RESET != EXECUTION CANCELLATION
    """
    provider_id = "test_provider_3"
    manager, health, failover, retry, sched = execution_environment
    _register_chain(manager, health, failover, retry, sched, provider_id)
    
    manager.record_execution(provider_id, RuntimeExecutionTrigger.MANUAL_EXECUTION)
    
    result = manager.clear_execution(provider_id)
    
    # Verify it returns preparation info and NOT a RuntimeExecutionResult
    assert isinstance(result, RuntimeExecutionPreparationResult)
    assert not isinstance(result, RuntimeExecutionResult)
    
    # Verify state is ABORTED, and NOT CANCELLED outcome
    assert result.execution_info.current_status == RuntimeExecutionStatus.ABORTED
    assert not hasattr(result.execution_info, 'outcome')
    
    # Prove ABORTED remains a RuntimeExecutionStatus
    assert isinstance(result.execution_info.current_status, RuntimeExecutionStatus)
    
    # Prove CANCELLED remains an execution outcome (distinct dimension)
    assert isinstance(RuntimeExecutionOutcome.CANCELLED, RuntimeExecutionOutcome)


def test_reset_does_not_execute_or_recover(execution_environment):
    """
    SCENARIO 4 — RESET DOES NOT AUTOMATICALLY EXECUTE OR RECOVER
    """
    provider_id = "test_provider_4"
    manager, health, failover, retry, sched = execution_environment
    _register_chain(manager, health, failover, retry, sched, provider_id)
    
    result = manager.clear_execution(provider_id)
    
    # 1. Runtime behavior proof
    # It returns structural preparation information
    assert isinstance(result, RuntimeExecutionPreparationResult)
    # It does not produce RuntimeExecutionResult
    assert not isinstance(result, RuntimeExecutionResult)
    # (By definition of its pure return type and observation, no workload execution or outcome occurred)
    
    # 2. Structural dependency proof
    # RuntimeExecutionManager has no constructor dependency on RuntimeExecutor or RuntimeExecutionCoordinator
    # We inspect the actual constructor signature of RuntimeExecutionManager
    init_params = inspect.signature(RuntimeExecutionManager.__init__).parameters
    
    assert "runtime_executor" not in init_params
    assert "executor" not in init_params
    assert "runtime_execution_coordinator" not in init_params
    assert "coordinator" not in init_params
    
    # Verify the only non-self dependency is RuntimeSchedulingManager
    dependency_count = len([p for name, p in init_params.items() if name != "self"])
    assert dependency_count == 1
    assert "runtime_scheduling_manager" in init_params


def test_historical_result_remains_immutable(execution_environment):
    """
    SCENARIO 5 — HISTORICAL RESULT REMAINS AN INDEPENDENT IMMUTABLE FACT
    """
    provider_id = "test_provider_5"
    manager, health, failover, retry, sched = execution_environment
    _register_chain(manager, health, failover, retry, sched, provider_id)
    
    # Construct a legitimate historical RuntimeExecutionResult
    identity = RuntimeExecutionIdentity(
        descriptor=RuntimeExecutionDescriptor("exec_5", "rt_1", "boot_1", "1.0", "1.0"),
        metadata=RuntimeExecutionMetadata("test", "test", datetime.utcnow(), datetime.utcnow(), frozenset(), MappingProxyType({"key": "val"}), "1.0"),
        status=RuntimeExecutionStatus.COMPLETED,
        snapshot=RuntimeExecutionSnapshot("1", "2", "3", "4", "5", "6")
    )
    
    started = datetime.utcnow()
    completed = datetime.utcnow()
    
    historical_result = RuntimeExecutionResult(
        identity=identity,
        outcome=RuntimeExecutionOutcome.SUCCESS,
        started_at=started,
        completed_at=completed,
        duration_seconds=2.5,
        metadata=MappingProxyType({"important": "fact"})
    )
    
    # Record relevant fields before reset
    orig_identity = historical_result.identity
    orig_outcome = historical_result.outcome
    orig_started = historical_result.started_at
    orig_completed = historical_result.completed_at
    orig_duration = historical_result.duration_seconds
    orig_reason = historical_result.failure_reason
    orig_metadata = historical_result.metadata
    
    # Perform clear_execution
    manager.clear_execution(provider_id)
    
    # Verify that the independently created RuntimeExecutionResult remains unchanged
    assert historical_result.identity is orig_identity
    assert historical_result.outcome == orig_outcome
    assert historical_result.started_at == orig_started
    assert historical_result.completed_at == orig_completed
    assert historical_result.duration_seconds == orig_duration
    assert historical_result.failure_reason == orig_reason
    assert historical_result.metadata == orig_metadata
    
    # Verify immutability (dataclass is frozen, assigning attributes raises FrozenInstanceError)
    with pytest.raises(dataclasses.FrozenInstanceError):
        historical_result.outcome = RuntimeExecutionOutcome.FAILED
