# Batch 6B.3.6: Capability Intent Preparation Report

## 1. Batch Objective
The primary objective of Batch 6B.3.6 was to establish the smallest correct Runtime-core orchestration boundary that transforms a `CapabilityRequest` into an `ExecutionIntent`. This establishes the Runtime's declarative PREPARATION flow without establishing execution planning, provider selection, or scheduling.

## 2. Existing Components Reused
The inspected implementation successfully reused the existing, protected components without modification:
- `CapabilityRequest` (from `backend/src/runtime/core/request.py`)
- `CapabilityResolver` (from `backend/src/runtime/core/capability_resolution.py`)
- `CapabilityDescriptor` (from `backend/src/runtime/core/capabilities.py`)
- `CapabilityIntentAssembler` (from `backend/src/runtime/core/intent_assembly.py`)
- `ExecutionIntent` (from `backend/src/runtime/core/intent.py`)

## 3. New Preparation Service Responsibility
A new component, `CapabilityIntentPreparationService`, was created. It is strictly responsible for coordinating capability resolution and intent assembly. It acts as an orchestration boundary and delegates all logic to injected dependencies (`CapabilityResolver` and `CapabilityIntentAssembler`).

## 4. Exact Flow
The exact flow established by the new boundary is:
1. Accept `CapabilityRequest` and an opaque payload.
2. Delegate to `CapabilityResolver.resolve(request)` to obtain a `CapabilityDescriptor`.
3. Delegate to `CapabilityIntentAssembler.assemble(descriptor, payload)` to obtain an `ExecutionIntent`.
4. Return the `ExecutionIntent`.

## 5. Capability Identity Preservation
The `CapabilityIntentPreparationService` preserves the authoritative identity chain. It does not construct or mutate capability IDs. The identity established by the `CapabilityDescriptor` returned by the resolver remains authoritative and is passed unaltered to the assembler.

## 6. Payload Opacity
The payload is treated as entirely opaque. The implementation does not inspect, validate, normalize, or transform the payload. It simply passes it from the method argument to the assembler.

## 7. Output-Contract Propagation
The implementation does not resolve or instantiate schemas. The output schema defined in the descriptor's metadata is handled completely by the `CapabilityIntentAssembler`. `CapabilityIntentPreparationService` introduces no Pydantic imports or schema registries.

## 8. Error Behavior
Unknown capability resolution naturally propagates `CapabilityResolutionError` from the `CapabilityResolver`. The preparation service does not swallow this exception, fabricate fallback intents, or attempt to mask knowledge failures with execution failures.

## 9. Provider Neutrality
No provider dependency was identified. The service does not import or know about `OllamaProvider`, `OpenAI`, `Gemini`, or `ProviderFactory`.

## 10. Hardware Neutrality
No hardware information is required or inspected. The boundary does not contain any logic for GPU, VRAM, RAM, or CPU awareness.

## 11. Planning Neutrality
No execution plans or strategies are constructed. The component acts strictly as a declarative preparation phase.

## 12. Execution Neutrality
No execution occurs. `RuntimeExecutor` is not invoked. The result of the service is a purely declarative `ExecutionIntent`.

## 13. Application Separation
No application integration was introduced. `CampaignIntelligenceService`, FastAPI routes, and application startup remain completely unaffected. The application currently bypasses this path.

## 14. 6B.2 Invariant Preservation
Sprint 6B.2 invariants remain strictly intact:
- `RuntimeContext` remains the composition root.
- The boundary does not introduce new composition roots.
- Application lifecycle remains separate from Runtime lifecycle.
- Operational lifecycle logic has not been moved into declarative models.

## 15. Exact Files Changed
Created files:
- `backend/src/runtime/core/capability_intent_preparation.py`
- `backend/tests/unit/runtime/core/test_capability_intent_preparation.py`
- `backend/tests/architecture/runtime/test_capability_intent_preparation_architecture.py`

No existing source files, test files, or application files were modified.

## 16. Test Results
The executed test suite reported:
- Focused unit tests for `CapabilityIntentPreparationService` passed.
- Architecture tests passed, confirming the absence of prohibited imports (providers, hardware, execution, application wiring).
- Unit runtime test suite (`backend/tests/unit/runtime/`) passed.

## 17. Failure Classification
The following failures were observed during the regression suite execution, all of which are evidence-based pre-existing carry-forward issues explicitly documented prior to this Batch:
- `test_one_component_one_artifact_mapping` (Architecture Certification)
- `test_decision_ownership_mapping` (Governance Certification)
- `test_pipeline_completeness_and_uniqueness` (Pipeline Certification)
- `NameError: name 'RenderPlan' is not defined` (in `test_render_e2e.py` during full suite collection)

None of these failures involve the newly established `capability_intent_preparation.py` boundary.

## 18. Current vs Target Runtime State
**Current State:** The Application continues to directly use `IAIService` -> `ProviderFactory` -> `OllamaProvider`. It bypasses this newly established preparation path.

**Target State:** The Runtime now possesses the initial segments of the declarative path (`CapabilityRequest` -> `CapabilityIntentPreparationService` -> `ExecutionIntent`). Future planning and execution routing components will be attached to this declarative intent in subsequent batches.

## 19. Explicit Non-Goals
Within the authorized scope, the implementation explicitly avoided:
- Modifying `RuntimeContext` or `RuntimeBootstrap`.
- Integrating `RuntimeExecutor`.
- Selecting or invoking providers (e.g., Ollama).
- Hardware discovery.
- Schema validation or serialization.

## 20. Handoff to Next Batch
The Runtime now possesses a coherent declarative preparation path from `CapabilityRequest` through capability resolution and intent assembly to `ExecutionIntent`. Execution planning, resource allocation, and actual execution routing remain future work to be implemented in subsequent batches.
