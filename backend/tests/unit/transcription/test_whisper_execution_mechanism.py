import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from contextlib import asynccontextmanager

from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.core.route_decision import RouteDecision
from src.runtime.execution.execution_result import ExecutionOutcome
from src.transcription.dtos import TranscriptionRequest, Transcript
from src.transcription.execution.workload import TranscriptionWorkload
from src.transcription.execution.mechanism import WhisperExecutionMechanism
from src.transcription.exceptions import TranscriptionProcessingError, TranscriptionConfigurationError
from src.transcription.interfaces import ITranscriptionService, ITranscriptRepository

@pytest.fixture
def mock_service():
    return AsyncMock(spec=ITranscriptionService)

@pytest.fixture
def mock_repo():
    return AsyncMock(spec=ITranscriptRepository)

@pytest.fixture
def mock_repo_factory(mock_repo):
    @asynccontextmanager
    async def factory():
        yield mock_repo
    return factory

@pytest.fixture
def dummy_workload():
    req = TranscriptionRequest(media_path="dummy.wav")
    return TranscriptionWorkload(request=req)

@pytest.fixture
def dummy_workload_with_video():
    req = TranscriptionRequest(
        media_path="dummy.wav",
        video_asset_id=uuid.uuid4()
    )
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

def test_whisper_mechanism_success_with_persistence(mock_service, mock_repo_factory, mock_repo, dummy_target, dummy_workload_with_video):
    # Setup
    mock_transcript = Transcript(full_text="Hello world", segments=[])
    mock_service.transcribe.return_value = mock_transcript

    mechanism = WhisperExecutionMechanism(mock_service, repo_factory=mock_repo_factory)

    # Execute
    outcome, error = mechanism.execute(dummy_target, dummy_workload_with_video)

    # Assert
    assert outcome == ExecutionOutcome.SUCCESS
    assert error is None
    mock_service.transcribe.assert_called_once_with(dummy_workload_with_video.request)
    
    # Verify EXACT object identity reaches persistence
    mock_repo.save_transcript.assert_called_once_with(
        dummy_workload_with_video.request.video_asset_id,
        mock_transcript
    )
    
    saved_transcript = mock_repo.save_transcript.call_args.args[1]
    assert saved_transcript is mock_transcript

def test_whisper_mechanism_success_missing_video_id(mock_service, mock_repo_factory, mock_repo, dummy_target, dummy_workload):
    # Setup
    mock_transcript = Transcript(full_text="Hello world", segments=[])
    mock_service.transcribe.return_value = mock_transcript

    mechanism = WhisperExecutionMechanism(mock_service, repo_factory=mock_repo_factory)

    # Execute
    outcome, error = mechanism.execute(dummy_target, dummy_workload)

    # Assert
    assert outcome == ExecutionOutcome.SUCCESS
    assert error is None
    mock_service.transcribe.assert_called_once_with(dummy_workload.request)
    # Verify persistence skipped
    mock_repo.save_transcript.assert_not_called()

def test_whisper_mechanism_persistence_failure_translates_to_failed(mock_service, mock_repo_factory, mock_repo, dummy_target, dummy_workload_with_video):
    # Setup
    mock_transcript = Transcript(full_text="Hello world", segments=[])
    mock_service.transcribe.return_value = mock_transcript
    mock_repo.save_transcript.side_effect = ValueError("Database connection lost")

    mechanism = WhisperExecutionMechanism(mock_service, repo_factory=mock_repo_factory)

    # Execute
    outcome, error = mechanism.execute(dummy_target, dummy_workload_with_video)

    # Assert
    assert outcome == ExecutionOutcome.FAILED
    assert "Database connection lost" in error

def test_whisper_mechanism_processing_error_translation(mock_service, dummy_target, dummy_workload):
    # Setup
    mock_service.transcribe.side_effect = TranscriptionProcessingError("Failed inference")
    mechanism = WhisperExecutionMechanism(mock_service)

    # Execute
    outcome, error = mechanism.execute(dummy_target, dummy_workload)

    # Assert
    assert outcome == ExecutionOutcome.FAILED
    assert error == "Failed inference"

def test_whisper_mechanism_configuration_error_translation(mock_service, dummy_target, dummy_workload):
    # Setup
    mock_service.transcribe.side_effect = TranscriptionConfigurationError("Invalid model")
    mechanism = WhisperExecutionMechanism(mock_service)

    # Execute
    outcome, error = mechanism.execute(dummy_target, dummy_workload)

    # Assert
    assert outcome == ExecutionOutcome.FAILED
    assert error == "Invalid model"

def test_whisper_mechanism_unexpected_error_propagation(mock_service, dummy_target, dummy_workload):
    # Setup
    mock_service.transcribe.side_effect = ValueError("Unexpected bug")
    mechanism = WhisperExecutionMechanism(mock_service)

    # Execute
    outcome, error = mechanism.execute(dummy_target, dummy_workload)

    # Assert
    assert outcome == ExecutionOutcome.FAILED
    assert "Unexpected bug" in error

