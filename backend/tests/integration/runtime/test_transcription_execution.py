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
def test_real_transcription_execution(dummy_wav_path):
    """
    Proves truthful end-to-end local execution of the Whisper provider.

    This integration test verifies:
    1. Normalizer translates intent via the composed boundary.
    2. Registry correctly maps the capability/provider to the mechanism via the composed engine.
    3. Mechanism successfully bridges the async thread boundary and runs faster-whisper natively.
    """
    # 1. Boot the actual container
    container = initialize_container()

    from src.runtime.execution.runtime_execution_boundary import RuntimeExecutionBoundary
    from src.runtime.execution.execution_engine import ExecutionEngine

    boundary = container.resolve(RuntimeExecutionBoundary)
    engine = container.resolve(ExecutionEngine)

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

    # 3. Construct target routing decisions (Runtime Core planning output mock)
    from src.runtime.core.planning_result import PlanningResult
    from src.runtime.core.policy_decision import PolicyDecision

    planning = PlanningResult(intent, "direct")
    policy = PolicyDecision(planning, True, "default", True)
    route = RouteDecision(policy, "local", True, True)

    target = ExecutionTarget(
        route_decision=route,
        target_id="local_whisper_1",
        target_class="local",
        provider="whisper"
    )

    # 4. Invoke the composed Runtime Execution Boundary
    # This allows the boundary to resolve the normalizer and construct ExecutionAdmission
    admission = boundary.execute(target, intent)

    # 5. Execute through the actual composed Runtime Engine
    # This proves ExecutionEngine -> Registry -> Mechanism -> Provider path
    result = engine.execute(admission)

    # 6. Assert genuine execution
    assert result.is_success is True, f"Whisper inference failed: {result.error_message}"
    assert result.error_message is None
    assert result.execution_target == target
