# BATCH 6B.5.7 IMPLEMENTATION PLAN — CONCRETE EXECUTION MECHANISM

## 1. Batch Identity
**Batch Name:** Concrete Execution Mechanism & Provider Adapter
**Objective:** Implement the FIRST REAL concrete execution mechanism behind the certified Milestone 6B execution architecture to prove truthful real execution without modifying certified boundaries.

## 2. Certified Baseline
**Baseline:** `milestone-6b-batch-6b.5.6`
**Commit:** `934165d60e8e611056a7aa325ed6376f7e86ba92`

## 3. Repository Evidence
- **Execution Architecture:** Fully certified synchronous boundaries via `ExecutionEngine`, `ExecutionMechanismRegistry`, and `AbstractExecutionMechanism`.
- **Existing Capabilities:** Found `AUDIO_TRANSCRIPTION` (Whisper) and `VIDEO_ANALYSIS` (LLM/Ollama).
- **Extension Points:** `ExecutionMechanismRegistry` and `WorkloadNormalizationExtensionPoint` exist to decouple routing from payload semantics.

## 4. Selected Capability
**Capability:** Transcription (`capability_id: "AUDIO_TRANSCRIPTION"`)

## 5. Capability Selection Rationale
Transcription provides the cleanest domain schema mapping (`TranscriptionRequest` -> `Transcript`) and avoids the stochastic API complexities, token-limit errors, and complex nested schema validation present in LLM-based Video Understanding. It offers a straightforward, deterministic input-to-output mapping that perfectly isolates the runtime boundary validation from the execution logic.

## 6. Selected Provider
**Provider:** Whisper (`provider_id: "whisper"`)

## 7. Provider Selection Rationale
`WhisperTranscriptionService` uses `faster-whisper`, executing strictly locally. This allows real execution to be proven in an integration test environment without relying on external SaaS API keys (like OpenAI) or separate running backend services (like an Ollama server). It only requires a local download of a small model (e.g., "tiny.en") and a dummy audio file.

## 8. Existing Provider Infrastructure
- **Provider Class:** `WhisperTranscriptionService` (in `src.transcription.providers.whisper_provider`)
- **Adapter Interface:** `ITranscriptionService`
- **Configuration:** `TranscriptionSettings`
- **Method:** `async def transcribe(request: TranscriptionRequest) -> Transcript`
- **Dependency:** `faster-whisper==1.0.3` is present in `requirements.txt`.

## 9. Existing Workload Schema
- **Schema:** `TranscriptionRequest` (in `src.transcription.dtos`)
- **Fields:** `media_path`, `language_hint`, `prompt`, `detect_speakers`
- It is a frozen Pydantic model representing immutable intent payload, but does not natively implement the `ExecutionWorkload` protocol property `capability_id`.

## 10. Concrete Workload
A lightweight domain-owned bridge class will be defined in `src/transcription/execution/workload.py`:
```python
from dataclasses import dataclass
from src.runtime.core.execution_workload import ExecutionWorkload
from src.transcription.dtos import TranscriptionRequest

@dataclass(frozen=True)
class TranscriptionWorkload(ExecutionWorkload):
    request: TranscriptionRequest

    @property
    def capability_id(self) -> str:
        return "AUDIO_TRANSCRIPTION"
```

## 11. Normalization Path
`ExecutionIntent.payload` → `TranscriptionNormalizer` → `TranscriptionWorkload` → `ExecutionAdmission`
- The `TranscriptionNormalizer` will parse the opaque payload (expected `dict`) into `TranscriptionRequest`, wrapping it in `TranscriptionWorkload`.
- It will be registered into the existing `WorkloadNormalizationExtensionPoint`.

## 12. Concrete Mechanism
**Class:** `WhisperExecutionMechanism` implementing `AbstractExecutionMechanism[TranscriptionWorkload]`
**Location:** `backend/src/transcription/execution/mechanism.py`
**Dependencies:** `ITranscriptionService`

## 13. Provider Translation
1. `WhisperExecutionMechanism` receives `ExecutionTarget` and `TranscriptionWorkload`.
2. Mechanism extracts `workload.request`.
3. Mechanism invokes `self._service.transcribe(workload.request)` via an async-to-sync thread bridge.
4. Returns `(True, None)` on success, or `(False, error_msg)` on expected provider failures.

## 14. ExecutionTarget Semantics
The mechanism receives `ExecutionTarget` but relies on the registry routing having already validated `target.provider == "whisper"`. The mechanism intentionally does not override the Whisper model size from the target because `WhisperTranscriptionService` currently tightly couples model size to `TranscriptionSettings` on instantiation. Target identity is passively preserved.

## 15. Mechanism Registry Registration
Key: `("whisper", "AUDIO_TRANSCRIPTION")`
Value: `MechanismRegistration(TranscriptionWorkload, WhisperExecutionMechanism(service))`

## 16. Normalizer Registration
Key: `"AUDIO_TRANSCRIPTION"`
Value: `TranscriptionNormalizer()`

## 17. Bootstrap / Composition
The mechanism and registry will be composed via DI in:
- `RuntimeModule` (`src/bootstrap/modules/runtime_module.py`): Provisions `ExecutionMechanismRegistry` and `WorkloadNormalizationExtensionPoint`. Resolves `ITranscriptionService` (registered by `InfrastructureModule`) to instantiate and register `WhisperExecutionMechanism`.
- `startup.py`: Modified to include `RuntimeModule`.
*(No separate transcription_module is needed since infrastructure_module already registers the service).*

## 18. Configuration Ownership
`TranscriptionSettings` retains ownership of Whisper configuration. No configuration leaks into `RuntimeExecutionBoundary`.

## 19. Sync / Async Strategy
`ExecutionEngine` is synchronous. `WhisperTranscriptionService.transcribe()` is asynchronous.
**Bridge Strategy:** The mechanism will execute the async `transcribe()` method safely inside a new thread using a local `threading.Thread` wrapper running `asyncio.run()`. This completely guarantees event-loop isolation from any parent ASGI runtime loop, preserving the certified synchronous boundary while preventing `RuntimeError`. Exceptions raised in the thread will be captured and re-raised in the calling thread.

## 20. Success Semantics
**SUCCESS =** `transcribe()` completes and returns a `Transcript` without raising an exception. This guarantees genuine local inference execution occurred.

## 21. Failure Semantics
Expected `TranscriptionProcessingError` and `TranscriptionConfigurationError` exceptions thrown by the provider are caught and translated to `(False, str(e))`. Unexpected errors propagate up.

## 22. Security Model
- No API keys are introduced or logged.
- The payload `media_path` is validated by Whisper (checks for `os.path.isfile`).
- The mechanism performs no subprocess calls (Faster-Whisper uses CTranslate2 bindings).

## 23. Legacy Isolation
The implementation avoids `RuntimeExecutor` entirely and adheres strictly to the Batch 6B.5.6 boundary.

## 24. Real Execution Proof
The integration test will generate a minimal 1-second WAV file and execute the runtime boundary, ensuring `faster-whisper` loads the `"tiny"` model and returns a valid `Transcript` object corresponding to the input. This definitively proves execution without mocks.

## 25. Test Strategy
- **Unit Tests:** `TranscriptionNormalizer` schema validation, and `WhisperExecutionMechanism` with mocks for async-to-sync error handling.
- **Integration Test:** Real execution through the container using the actual `faster-whisper` library.
- **Architecture Tests:** Validate no provider imports leak into Runtime Core.

## 26. Exact Production Files
**PRODUCTION — CREATE**
1. `backend/src/transcription/execution/__init__.py`
2. `backend/src/transcription/execution/workload.py`
3. `backend/src/transcription/execution/normalizer.py`
4. `backend/src/transcription/execution/mechanism.py`
5. `backend/src/bootstrap/modules/runtime_module.py`

**PRODUCTION — MODIFY**
1. `backend/src/bootstrap/startup.py`

*(Total Production Files: 6)*

## 27. Exact Test Files
**TEST — CREATE**
1. `backend/tests/unit/transcription/test_whisper_execution_mechanism.py`
2. `backend/tests/integration/runtime/test_transcription_execution.py`

**TEST — MODIFY**
*(None)*

*(Total Test Files: 2)*

## 28. Exact Documentation Files
**DOCUMENTATION — CREATE**
1. `backend/docs/certification/BATCH_6B_5_7_CONCRETE_EXECUTION_MECHANISM_REPORT.md`
2. `backend/docs/certification/BATCH_6B_5_7_PROVIDER_ENVIRONMENT_DIAGNOSTIC_REPORT.md`
3. `backend/docs/certification/BATCH_6B_5_7_PROVIDER_ENVIRONMENT_RECOVERY_REPORT.md`
4. `backend/docs/certification/BATCH_6B_5_7_PRODUCTION_ENVIRONMENT_CORRECTION_REPORT.md`

**DOCUMENTATION — MODIFY**
1. `backend/implementation_plan.md`

*(Total Documentation Files: 2)*

## 29. Exact Protected Files
Unless authorized, DO NOT MODIFY:
- `backend/src/runtime/core/intent.py`
- `backend/src/runtime/core/execution_target.py`
- `backend/src/runtime/core/planning_result.py`
- `backend/src/runtime/core/policy_decision.py`
- `backend/src/runtime/core/route_decision.py`
- `backend/src/runtime/core/capabilities.py`
- `backend/src/runtime/core/provider_capability_registry.py`
- `backend/src/runtime/core/providers.py`
- `backend/src/runtime/core/executor.py`
- `backend/src/runtime/core/execution_model.py`
- `backend/src/runtime/core/execution_workload.py`
- `backend/src/runtime/execution/workload_normalizer.py`
- `backend/src/runtime/execution/execution_admission.py`
- `backend/src/runtime/execution/runtime_execution_boundary.py`
- `backend/src/runtime/execution/execution_engine.py`
- `backend/src/runtime/execution/execution_mechanism_registry.py`
- `backend/src/runtime/execution/workload_normalization_extension.py`

## 30. Exact Change Budget
- Total Production: 6
- Total Test: 2
- Total Documentation: 2
- **TOTAL FILES: 10**

Zero unauthorized cleanup or modifications outside this budget.

## 31. Verification Commands
`pytest backend/tests/unit/transcription/test_whisper_execution_mechanism.py -v`
`pytest backend/tests/integration/runtime/test_transcription_execution.py -v`
`pytest backend/tests/architecture/runtime/ -v`

## 32. Stop Conditions
STOP if ExecutionEngine requires async conversion.
STOP if Whisper transcription blocks execution beyond testability constraints.
STOP if any protected boundary file modification is required.
STOP if `ExecutionWorkload` requires capability-specific fields inside the core abstraction.

## 33. Batch 6B.5.8 Handoff
Upon completion of this Batch, the Runtime will be verified as capable of transporting strongly-typed capabilities cleanly. Batch 6B.5.8 will generalize the async execution pooling or integrate routing telemetry.

## 34. Final Planning Decision
COMPLETE — REAL EXECUTION PROVEN (Batch 6B.5.7 Implementation Complete)
