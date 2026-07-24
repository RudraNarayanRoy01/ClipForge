from dataclasses import FrozenInstanceError
import pytest
from typing import Any

from src.runtime.core.context import RuntimeContext
from src.runtime.core.orchestrator import (
    ExecutionSession,
    SessionValidationStatus,
    StageExecutionState,
    StageOrchestrationStatus
)
from src.runtime.core.execution_engine import (
    RuntimeExecutionEngine,
    ExecutionResult,
    StageExecutionResult,
    ExecutionStatus
)


def test_stage_execution_result_is_immutable():
    """Verify StageExecutionResult cannot be modified after creation."""
    result = StageExecutionResult(
        stage_identifier="stage-1",
        stage_name="Stage 1",
        status=ExecutionStatus.COMPLETED
    )
    
    with pytest.raises(FrozenInstanceError):
        result.stage_name = "Modified Stage"  # type: ignore


def test_execution_result_is_immutable():
    """Verify ExecutionResult cannot be modified after creation."""
    result = ExecutionResult(
        session_id="session-1",
        stage_results=[],
        status=ExecutionStatus.COMPLETED
    )
    
    with pytest.raises(FrozenInstanceError):
        result.status = ExecutionStatus.FAILED  # type: ignore


def test_execution_result_contains_only_execution_info():
    """
    Architectural test: Verify ExecutionResult does not contain monitoring,
    optimization, adaptive, scheduling, provider, or resource allocation fields.
    """
    result = ExecutionResult(session_id="session-1")
    
    fields = dir(result)
    forbidden_terms = [
        "monitor", "metric", "optimiz", "adapt", "schedul", 
        "provider", "alloc", "hardware", "learn"
    ]
    
    for field in fields:
        if field.startswith("_"):
            continue
            
        for term in forbidden_terms:
            assert term not in field.lower(), f"ExecutionResult contains forbidden field: {field}"


def test_stage_execution_result_contains_only_execution_info():
    """
    Architectural test: Verify StageExecutionResult does not contain monitoring,
    optimization, adaptive, scheduling, provider, or resource allocation fields.
    """
    result = StageExecutionResult(
        stage_identifier="1", 
        stage_name="test", 
        status=ExecutionStatus.COMPLETED
    )
    
    fields = dir(result)
    forbidden_terms = [
        "monitor", "metric", "optimiz", "adapt", "schedul", 
        "provider", "alloc", "hardware", "learn"
    ]
    
    for field in fields:
        if field.startswith("_"):
            continue
            
        for term in forbidden_terms:
            assert term not in field.lower(), f"StageExecutionResult contains forbidden field: {field}"


def test_runtime_context_exposes_execution_engine():
    """Verify RuntimeContext acts as the Composition Root for Execution Engine."""
    context = RuntimeContext()
    
    assert hasattr(context, "execution_engine")
    assert isinstance(context.execution_engine, RuntimeExecutionEngine)
    

def test_execution_engine_consumes_session_and_produces_result():
    """Verify Execution Engine consumes immutable ExecutionSession and produces immutable ExecutionResult."""
    context = RuntimeContext()
    engine = context.execution_engine
    
    # Create an immutable session with two ready stages
    stage1 = StageExecutionState(
        stage_identifier="extract-audio",
        stage_name="Audio Extraction",
        dependency_readiness=StageOrchestrationStatus.READY,
        allocation_reference="alloc-1"
    )
    
    stage2 = StageExecutionState(
        stage_identifier="transcribe",
        stage_name="Transcription",
        dependency_readiness=StageOrchestrationStatus.READY,
        allocation_reference="alloc-2"
    )
    
    session = ExecutionSession(
        validation_status=SessionValidationStatus.VALID,
        stage_states=[stage1, stage2]
    )
    
    result = engine.execute_session(session)
    
    assert isinstance(result, ExecutionResult)
    assert result.status == ExecutionStatus.COMPLETED
    assert len(result.stage_results) == 2
    
    # Verify deterministic ordering preservation
    assert result.stage_results[0].stage_identifier == "extract-audio"
    assert result.stage_results[1].stage_identifier == "transcribe"
    assert result.stage_results[0].status == ExecutionStatus.COMPLETED
    assert result.stage_results[1].status == ExecutionStatus.COMPLETED


def test_execution_engine_handles_invalid_or_empty_session():
    """Verify Execution Engine safely handles empty sessions."""
    context = RuntimeContext()
    engine = context.execution_engine
    
    empty_session = ExecutionSession(
        validation_status=SessionValidationStatus.INCOMPLETE_CONTEXT,
        stage_states=[]
    )
    
    result = engine.execute_session(empty_session)
    
    assert isinstance(result, ExecutionResult)
    assert result.status == ExecutionStatus.FAILED
    assert result.session_id == "invalid-session"


def test_execution_engine_respects_orchestration_status():
    """Verify Execution Engine executes exactly what was prepared (simulated for now)."""
    context = RuntimeContext()
    engine = context.execution_engine
    
    stage1 = StageExecutionState(
        stage_identifier="ready-stage",
        stage_name="Ready",
        dependency_readiness=StageOrchestrationStatus.READY,
        allocation_reference="alloc-1"
    )
    
    stage2 = StageExecutionState(
        stage_identifier="blocked-stage",
        stage_name="Blocked",
        dependency_readiness=StageOrchestrationStatus.WAITING_FOR_DEPENDENCIES,
        allocation_reference="alloc-2"
    )
    
    session = ExecutionSession(
        validation_status=SessionValidationStatus.VALID,
        stage_states=[stage1, stage2]
    )
    
    result = engine.execute_session(session)
    
    # Since one stage wasn't READY, the simulated mock engine marks it NOT_STARTED 
    # and the overall execution as FAILED to indicate incomplete execution.
    assert result.status == ExecutionStatus.FAILED
    assert len(result.stage_results) == 2
    
    assert result.stage_results[0].stage_identifier == "ready-stage"
    assert result.stage_results[0].status == ExecutionStatus.COMPLETED
    
    assert result.stage_results[1].stage_identifier == "blocked-stage"
    assert result.stage_results[1].status == ExecutionStatus.NOT_STARTED
