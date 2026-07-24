import pytest
from dataclasses import FrozenInstanceError

from src.runtime.core.execution_context import (
    ContextValidationStatus,
    StageExecutionContext,
    ExecutionContext
)
from src.runtime.core.orchestrator import (
    StageOrchestrationStatus,
    SessionValidationStatus,
    StageExecutionState,
    ExecutionSession,
    RuntimeOrchestrator
)
from src.runtime.core.context import RuntimeContext


def test_stage_execution_state_immutability():
    """Verify StageExecutionState is immutable to protect architectural boundaries."""
    state = StageExecutionState(
        stage_identifier="test-stage-1",
        stage_name="Test Stage",
        dependency_readiness=StageOrchestrationStatus.READY,
        allocation_reference="test-stage-1",
        capability_requirements=["CUDA"],
        orchestration_metadata={"source": "test"}
    )
    
    with pytest.raises(FrozenInstanceError):
        state.stage_identifier = "mutated"
        
    with pytest.raises(FrozenInstanceError):
        state.orchestration_metadata = {}


def test_execution_session_immutability():
    """Verify ExecutionSession is immutable to protect architectural boundaries."""
    session = ExecutionSession(
        validation_status=SessionValidationStatus.VALID,
        stage_states=[],
        orchestration_metadata={"source": "test"}
    )
    
    with pytest.raises(FrozenInstanceError):
        session.validation_status = SessionValidationStatus.INVALID_SESSION
        
    with pytest.raises(FrozenInstanceError):
        session.orchestration_metadata = {}


def test_runtime_context_exposes_orchestrator():
    """Verify RuntimeContext owns and exposes RuntimeOrchestrator."""
    context = RuntimeContext()
    assert hasattr(context, 'orchestrator')
    
    orchestrator = context.orchestrator
    assert isinstance(orchestrator, RuntimeOrchestrator)
    assert orchestrator is context.orchestrator  # Should return the same instance


def test_orchestrator_consumes_execution_context():
    """Verify orchestrator successfully consumes valid ExecutionContext and produces ExecutionSession."""
    stage_contexts = [
        StageExecutionContext(
            stage_identifier="stage-1",
            stage_name="Stage 1",
            allocation_reference="alloc-1",
            dependency_references=[],
            capability_requirements=["CPU"]
        ),
        StageExecutionContext(
            stage_identifier="stage-2",
            stage_name="Stage 2",
            allocation_reference="alloc-2",
            dependency_references=["stage-1"],
            capability_requirements=["CUDA"]
        )
    ]
    
    execution_context = ExecutionContext(
        validation_status=ContextValidationStatus.VALID,
        stage_contexts=stage_contexts,
        preparation_metadata={}
    )
    
    orchestrator = RuntimeOrchestrator()
    session = orchestrator.create_session(execution_context)
    
    assert isinstance(session, ExecutionSession)
    assert session.validation_status == SessionValidationStatus.VALID
    assert len(session.stage_states) == 2
    
    # Verify mapping and dependency readiness
    assert session.stage_states[0].stage_identifier == "stage-1"
    assert session.stage_states[0].dependency_readiness == StageOrchestrationStatus.READY
    
    assert session.stage_states[1].stage_identifier == "stage-2"
    assert session.stage_states[1].dependency_readiness == StageOrchestrationStatus.WAITING_FOR_DEPENDENCIES


def test_orchestrator_detects_incomplete_context():
    """Verify orchestrator architectural validation detects incomplete context input."""
    # Create an invalid context
    invalid_context = ExecutionContext(
        validation_status=ContextValidationStatus.INCOMPLETE_ALLOCATION,
        stage_contexts=[],
        preparation_metadata={}
    )
    
    orchestrator = RuntimeOrchestrator()
    session = orchestrator.create_session(invalid_context)
    
    assert session.validation_status == SessionValidationStatus.INCOMPLETE_CONTEXT
    assert len(session.stage_states) == 0


def test_orchestrator_detects_invalid_dependency_ordering():
    """Verify orchestrator validation catches invalid dependency references."""
    stage_contexts = [
        StageExecutionContext(
            stage_identifier="stage-1",
            stage_name="Stage 1",
            allocation_reference="alloc-1",
            dependency_references=["non-existent-stage"],
            capability_requirements=["CPU"]
        )
    ]
    
    execution_context = ExecutionContext(
        validation_status=ContextValidationStatus.VALID,
        stage_contexts=stage_contexts,
        preparation_metadata={}
    )
    
    orchestrator = RuntimeOrchestrator()
    session = orchestrator.create_session(execution_context)
    
    assert session.validation_status == SessionValidationStatus.INVALID_DEPENDENCY


def test_execution_session_contains_no_execution_state():
    """Verify architectural boundaries: session must not contain execution or hardware state."""
    stage_contexts = [
        StageExecutionContext(
            stage_identifier="stage-1",
            stage_name="Stage 1",
            allocation_reference="alloc-1",
            dependency_references=[],
            capability_requirements=[]
        )
    ]
    
    execution_context = ExecutionContext(
        validation_status=ContextValidationStatus.VALID,
        stage_contexts=stage_contexts
    )
    
    orchestrator = RuntimeOrchestrator()
    session = orchestrator.create_session(execution_context)
    
    # Assert properties don't exist
    assert not hasattr(session, "execution_state")
    assert not hasattr(session, "execution_results")
    assert not hasattr(session, "provider_instances")
    assert not hasattr(session, "hardware_handles")
    assert not hasattr(session, "gpu_identifiers")
    assert not hasattr(session, "cpu_identifiers")
    assert not hasattr(session, "runtime_metrics")
    assert not hasattr(session, "monitoring_information")
    assert not hasattr(session, "optimization_information")
    assert not hasattr(session, "ai_outputs")
    
    for stage_state in session.stage_states:
        assert not hasattr(stage_state, "execution_state")
        assert not hasattr(stage_state, "execution_results")
        assert not hasattr(stage_state, "provider_instances")
        assert not hasattr(stage_state, "hardware_handles")
        assert not hasattr(stage_state, "physical_gpu")
        assert not hasattr(stage_state, "physical_cpu")
        assert not hasattr(stage_state, "physical_ram")
        assert not hasattr(stage_state, "hardware_identifiers")
        assert not hasattr(stage_state, "cuda_objects")
        assert not hasattr(stage_state, "vulkan_objects")
        assert not hasattr(stage_state, "directml_objects")
        assert not hasattr(stage_state, "monitoring_information")
        assert not hasattr(stage_state, "optimization_information")
