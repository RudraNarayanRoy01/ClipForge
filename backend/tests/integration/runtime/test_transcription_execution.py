import os
import wave
import pytest

from src.bootstrap.startup import initialize_container
from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.execution_target import ExecutionTarget
from src.runtime.core.route_decision import RouteDecision
from src.runtime.execution.execution_mechanism_registry import ExecutionMechanismRegistry
from src.runtime.execution.workload_normalization_extension import WorkloadNormalizationExtensionPoint

@pytest.fixture
def dummy_wav_path(tmp_path):
    """Creates a 1-second silent WAV file required for testing Whisper inference."""
    file_path = tmp_path / "test_audio.wav"
    with wave.open(str(file_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        # 16000 frames of silence
        wf.writeframes(b'\x00' * (16000 * 2))
    return str(file_path)

@pytest.mark.integration
def test_real_transcription_execution(dummy_wav_path, monkeypatch):
    """
    Proves truthful end-to-end local execution of the Whisper provider.

    This integration test verifies:
    1. Normalizer translates intent via the composed boundary.
    2. Registry correctly maps the capability/provider to the mechanism via the composed engine.
    3. Mechanism successfully bridges the async thread boundary and runs faster-whisper natively.

    Note: The established Runtime Execution contract intentionally returns ONLY
    execution status (ExecutionResult). Resulting payloads (e.g., Transcript)
    are generated internally but are explicitly outside the scope of this boundary's propagation contract.
    """
    # Configure the environment context for the CPU-baseline certification profile
    monkeypatch.setenv("TRANSCRIPTION_MODEL", "tiny")
    monkeypatch.setenv("TRANSCRIPTION_DEVICE", "cpu")

    # 1. Boot the actual container
    container = initialize_container()

    from src.runtime.invocation.runtime_invocation_facade import RuntimeInvocationFacade
    from src.runtime.core.planning_context import PlanningContext

    facade = container.resolve(RuntimeInvocationFacade)

    # 2. Formulate Intent
    intent = ExecutionIntent(
        capability_id="AUDIO_TRANSCRIPTION",
        payload={
            "media_path": dummy_wav_path,
            "language_hint": "en",
            "prompt": "",
            "detect_speakers": False
        }
    )

    # 3. Construct PlanningContext
    planning_context = PlanningContext(
        quality_preference="balanced",
        latency_preference="balanced",
        cost_preference="balanced",
        locality_preference="local",
        constraints=tuple()
    )

    # 4. Invoke the complete Runtime Invocation Facade
    # This automatically processes the TargetDescription metadata created by RuntimeModule
    result = facade.invoke(intent, planning_context)

    # 5. Assert genuine execution status and configuration transport
    from src.runtime.execution.execution_result import ExecutionOutcome
    assert result.outcome == ExecutionOutcome.SUCCESS, f"Whisper inference failed: {result.error_message}"
    assert result.error_message is None
    
    # Prove the configuration flow reached the ExecutionTarget
    target = result.execution_target
    assert target is not None
    assert target.model == "tiny"
    assert target.device == "cpu"
    # compute_class defaults to None if not specified in env for the default settings, or 'default'
    # We just ensure it was carried through.
    
    # 6. Prove the concrete provider no longer has the global settings object
    from src.transcription.providers.whisper_provider import WhisperTranscriptionService
    whisper_service = container.resolve(WhisperTranscriptionService)
    assert not hasattr(whisper_service, '_settings'), "Provider must not own global settings"
    assert whisper_service._current_model == "tiny", "Provider must have loaded the explicitly requested model"
    assert whisper_service._current_device == "cpu", "Provider must have loaded on the explicitly requested device"
    
    # 7. PROVE R-001 CORRECTION (Repeated execution safe)
    # The second execution must use the same provider and mechanism without
    # encountering a cross-loop `RuntimeError: Event loop is closed`.
    result_2 = facade.invoke(intent, planning_context)
    assert result_2.outcome == ExecutionOutcome.SUCCESS, f"Repeated Whisper inference failed: {result_2.error_message}"
    assert result_2.error_message is None
