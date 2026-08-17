# Batch 6B.3.7 — Intent Validation Boundary

## 1. Objective
This Batch establishes the structural validation boundary between `ExecutionIntent` preparation and the future Runtime Planning layer. The validator serves as a deterministic gate to ensure only structurally valid intents enter the next Runtime phase, strictly preserving the declarative nature of the intent without anticipating how it will execute.

## 2. Repository Evidence
A critical repository inspection of `backend/src/` identified existing validation abstractions such as `ExecutionValidationException` and `runtime_execution_dispatcher_validator.py`. These were rejected because they are dedicated to execution graphs, dispatch routing, and lifecycle validation. Application-level validation exceptions (e.g., `TranscriptValidationError`, `VideoUnderstandingValidationError`) exist in the domain layer. There was no existing boundary validator for an `ExecutionIntent`.

## 3. CREATE Decision
Because reusing existing execution or domain validation abstractions would inappropriately mix intent validation with execution mechanics or application semantics, a dedicated Runtime-core validator was created.

## 4. Validator Contract
```python
class IntentValidationError(Exception):
    pass

class ExecutionIntentValidator:
    def validate(self, intent: Any) -> None:
        ...
```
This is a simple exception-based contract. Validation success returns `None`. Failure raises `IntentValidationError`.

## 5. Validation Rules
- **Input Type**: Enforced using `isinstance(intent, ExecutionIntent)`.
- **Capability ID**: `intent.capability_id` must be a non-empty string not composed solely of whitespace.
- **Output Contract**: `intent.output_contract` must be `None` or a non-empty string not composed solely of whitespace.

## 6. Payload Opacity
Payload admissibility is intentionally outside the Runtime intent-validation contract because payload semantics belong strictly to the capability/application domain. The validator imposes no structural or type checks on `payload`.

## 7. Output Contract
`intent.output_contract` is structurally checked only. It is treated as a descriptive string identifier. The validator does not instantiate it, register it, resolve it, or translate it into provider parameters.

## 8. Error Semantics
- `CapabilityResolutionError`: Raised when the Runtime does not know the requested capability.
- `IntentValidationError`: Raised when the capability is known, but the prepared intent violates the Runtime's structural entry conditions.

## 9. Neutrality
The `ExecutionIntentValidator` maintains absolute architectural neutrality:
- **Provider Neutrality**: No imports or usage of Ollama, OpenAI, Gemini, or `ProviderFactory`.
- **Hardware Neutrality**: No references to GPU, CUDA, RAM, or hardware capacity.
- **Planning Neutrality**: No usage of `ExecutionPlanner`, `ExecutionPlan`, or routing policies.
- **Scheduling/Execution Neutrality**: No usage of `scheduler`, queues, retries, or `RuntimeExecutor`.
- **Application/Schema Neutrality**: No dependency on FastAPI, application intelligence services, Pydantic serialization, or domain schemas like `ExtractionSummarySchema`.

## 10. Tests
- **Unit tests**: `pytest backend/tests/unit/runtime/core/test_intent_validation.py -v --tb=short` passed successfully (16 tests).
- **Architecture test**: `pytest backend/tests/architecture/runtime/test_intent_validation_architecture.py -v --tb=short` passed successfully, confirming strict AST-level absence of forbidden architectural imports.
- **Runtime architecture suite**: `pytest backend/tests/architecture/runtime/ -v --tb=short` passed.
- **Runtime regression suite**: `pytest backend/tests/runtime/ -v --tb=short` (reported 51 passed, 3 pre-existing failures).
- **Full backend suite**: `pytest backend/tests/ -v --tb=short`

## 11. Existing Failures
The following carry-forward failures were observed during the runtime regression test and confirmed to exist at the Batch baseline (as documented in the Batch specification):
- `test_one_component_one_artifact_mapping`
- `test_decision_ownership_mapping`
- `test_pipeline_completeness_and_uniqueness`
These represent known certification reporting issues not caused by Batch 6B.3.7.

## 12. Current vs Target
- **CURRENT**: Application AI execution still bypasses Runtime execution, utilizing direct ProviderFactory routes.
- **TARGET AFTER THIS BATCH**: Validated declarative intents can now serve as a guaranteed structural input boundary for the future Planning layer.

## 13. Scope
**Added**:
- `backend/src/runtime/core/intent_validation.py`
- `backend/tests/unit/runtime/core/test_intent_validation.py`
- `backend/tests/architecture/runtime/test_intent_validation_architecture.py`
- `backend/docs/certification/BATCH_6B_3_7_INTENT_VALIDATION_BOUNDARY_REPORT.md`

**Modified**: 0 existing files.

## 14. 6B.2 Invariants
The implementation strictly preserves Provider abstraction, Hardware abstraction, Application/Runtime separation, and the frozen status of `ExecutionIntent`.

## 15. Git Integrity
Confirmed: No commits, no tags, no resets, no rebases, no amends, no history rewrites were performed. The working tree reflects only the explicitly authorized additions.

## 16. Remaining Work
Planning, scheduling, provider selection, hardware selection, execution mechanics, and application integration remain untouched and are designated for future Runtime work.
