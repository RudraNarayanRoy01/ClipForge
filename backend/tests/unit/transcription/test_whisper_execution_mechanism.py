import pytest
from unittest.mock import AsyncMock, patch

from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.core.route_decision import RouteDecision
from src.transcription.dtos import TranscriptionRequest
from src.transcription.execution.workload import TranscriptionWorkload
from src.transcription.execution.mechanism import WhisperExecutionMechanism
from src.transcription.exceptions import TranscriptionProcessingError, TranscriptionConfigurationError
from src.transcription.interfaces import ITranscriptionService

@pytest.fixture
def mock_service():
    return AsyncMock(spec=ITranscriptionService)

@pytest.fixture
def dummy_workload():
    req = TranscriptionRequest(media_path="dummy.wav")
    return TranscriptionWorkload(request=req)

@pytest.fixture
def dummy_target():
    from src.runtime.core.intent import ExecutionIntent
    from src.runtime.core.planning_result import PlanningResult
    from src.runtime.core.policy_decision import PolicyDecision

    intent = ExecutionIntent(capability_id="AUDIO_TRANSCRIPTION", payload={})
    planning = PlanningResult(intent, "direct")
    policy = PolicyDecision(planning, True, "default", True)
    route = RouteDecision(policy, "local", True, True)

    return ExecutionTarget(
        route_decision=route,
        target_id="target_1",
        target_class="local",
        provider="whisper"
    )

def test_whisper_mechanism_success(mock_service, dummy_target, dummy_workload):
    # Setup
    mock_transcript = {"text": "Hello world"}
    mock_service.transcribe.return_value = mock_transcript

    mechanism = WhisperExecutionMechanism(mock_service)

    # Execute
    success, error = mechanism.execute(dummy_target, dummy_workload)

    # Assert
    assert success is True
    assert error is None
    mock_service.transcribe.assert_called_once_with(dummy_workload.request)

def test_whisper_mechanism_processing_error_translation(mock_service, dummy_target, dummy_workload):
    # Setup
    mock_service.transcribe.side_effect = TranscriptionProcessingError("Failed inference")
    mechanism = WhisperExecutionMechanism(mock_service)

    # Execute
    success, error = mechanism.execute(dummy_target, dummy_workload)

    # Assert
    assert success is False
    assert error == "Failed inference"

def test_whisper_mechanism_configuration_error_translation(mock_service, dummy_target, dummy_workload):
    # Setup
    mock_service.transcribe.side_effect = TranscriptionConfigurationError("Invalid model")
    mechanism = WhisperExecutionMechanism(mock_service)

    # Execute
    success, error = mechanism.execute(dummy_target, dummy_workload)

    # Assert
    assert success is False
    assert error == "Invalid model"

def test_whisper_mechanism_unexpected_error_propagation(mock_service, dummy_target, dummy_workload):
    # Setup
    mock_service.transcribe.side_effect = ValueError("Unexpected bug")
    mechanism = WhisperExecutionMechanism(mock_service)

    # Execute and Assert
    with pytest.raises(ValueError, match="Unexpected bug"):
        mechanism.execute(dummy_target, dummy_workload)
