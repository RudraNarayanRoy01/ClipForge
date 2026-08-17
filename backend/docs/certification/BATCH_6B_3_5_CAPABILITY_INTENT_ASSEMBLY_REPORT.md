# BATCH 6B.3.5 CAPABILITY INTENT ASSEMBLY REPORT

## 1. Batch Objective
Establish the canonical Runtime-core mechanism (`CapabilityIntentAssembler`) that converts a successfully resolved `CapabilityDescriptor` plus opaque workload data into an immutable `ExecutionIntent`. This forms the assembly boundary before any future execution planning occurs.

## 2. Repository Evidence
Inspection of the following Runtime files was performed:
- `capabilities.py`: Defines `CapabilityDescriptor` and registry.
- `capability_resolution.py`: Defines the resolver answering "is this capability known?"
- `request.py`: Defines the provider-neutral `CapabilityRequest`.
- `intent.py`: Defines `ExecutionIntent` with fields `capability_id`, `payload`, and `output_contract`.
- `context.py`: Defines the central Runtime composition root.
- `bootstrap.py`: Defines Runtime initialization.
- `executor.py`: Defines the ultimate execution mechanism.

## 3. Existing Abstraction Analysis
No existing equivalent assembler or factory was found that converts a capability and payload into an `ExecutionIntent`. `ExecutionIntent` was defined as a dataclass without an explicit native factory. 

## 4. Why CapabilityIntentAssembler was Created
Since no existing core abstraction assumed this responsibility, `CapabilityIntentAssembler` was explicitly created as the canonical mechanism to construct an `ExecutionIntent`.

## 5. Exact Contract
The implemented contract is purely assembly:
```python
class CapabilityIntentAssembler:
    def assemble(self, descriptor: CapabilityDescriptor, payload: Any) -> ExecutionIntent:
        ...
```
It accepts an already-resolved `CapabilityDescriptor` and an opaque payload. It returns an `ExecutionIntent`.

## 6. Capability Identity Propagation
The capability identity is obtained exclusively from `descriptor.identifier`. The caller cannot override or provide a separate identifier, ensuring the resolved descriptor remains authoritative.

## 7. Output Contract Propagation
If the descriptor specifies an `output_schema` within its `metadata` (e.g., `"ExtractionSummarySchema"`), this string is passed to `ExecutionIntent.output_contract`. The implementation strictly treats this as descriptive metadata propagation. It does not instantiate schemas, validate them, or import validation frameworks.

## 8. Payload Semantics
The `payload` parameter is annotated as `Any` and passed directly to the `ExecutionIntent` without transformation. It remains an opaque caller-provided workload representation.

## 9. Provider Neutrality
The inspected implementation has no imports or dependencies on `ollama`, `openai`, `gemini`, or `ProviderFactory`.

## 10. Hardware Neutrality
No dependencies exist regarding `CUDA`, `GPU`, or resource discovery. The assembler does not represent hardware.

## 11. Execution Neutrality
The assembler has no imports for `RuntimeExecutor` or `RuntimeExecutionResult`. It does not execute logic, queue work, or initiate network calls.

## 12. Planning Neutrality
The assembled intent does not contain planning strategy or policy data. It strictly answers what capability is requested, leaving how it executes to future planners.

## 13. Application Separation
No changes were made to the core application (e.g., `CampaignIntelligenceService`, `ImportCampaignUseCase`). The AI usage path in the application remains structurally bypassed for this batch.

## 14. 6B.2 Invariant Preservation
- `RuntimeContext` and its 23/17 boundary remained unmodified.
- `RuntimeExecutionContext` remained completely unmodified.
- The composition root was not touched to accommodate this batch.

## 15. Tests Executed
The following test suites were executed:
- `pytest backend/tests/unit/runtime/core/test_intent_assembly.py`
- `pytest backend/tests/architecture/runtime/`
- `pytest backend/tests/runtime/`

## 16. Exact Test Results
- Focused tests (`test_intent_assembly.py`): 10 passed
- Architecture tests (`test_intent_assembly_architecture.py` & existing architecture): 49 passed
- Runtime certification tests (`tests/runtime/`): 3 failed, 51 passed

## 17. Any Pre-Existing Failures
The 3 failures in `pytest backend/tests/runtime/` are identified as pre-existing/carry-forward failures:
1. `test_runtime_architecture_certification.py::test_one_component_one_artifact_mapping`
2. `test_runtime_governance_certification.py::TestOwnershipRules::test_decision_ownership_mapping`
3. `test_runtime_pipeline_certification.py::TestRuntimePipelineCertification::test_pipeline_completeness_and_uniqueness`

These relate to overarching runtime artifact mapping rules and pipeline completeness which are naturally impacted by the ongoing additions in Sprint 6B but fall outside the exact isolated change budget of 6B.3.5.

## 18. Change-Set Scope
- Added `backend/src/runtime/core/intent_assembly.py`
- Added `backend/tests/unit/runtime/core/test_intent_assembly.py`
- Added `backend/tests/architecture/runtime/test_intent_assembly_architecture.py`
- Modified 0 existing source files.
- Modified 0 existing test files.

## 19. Current vs Target State
**CURRENT APPLICATION:** 
Application AI execution bypasses Runtime.

**CURRENT RUNTIME:**
```text
CapabilityRequest
      ↓
CapabilityResolver
      ↓
CapabilityDescriptor
      ↓
CapabilityIntentAssembler
      ↓
ExecutionIntent
```

**TARGET (Future Architecture):**
```text
ExecutionIntent
      ↓
Execution Planner
      ↓
Policy / Strategy
      ↓
Provider / Resource Selection
      ↓
Scheduler
      ↓
RuntimeExecutor
      ↓
Provider
```

## 20. Future Batch Handoff
Batch 6B.3.6 will assume consumption of the `ExecutionIntent`. It must not assume that provider selection, hardware assignment, scheduling, or actual execution exist. The boundary handed off is exclusively the declarative declarative intent.

## 21. Remaining Carry-Forward Issues
The three certification test mapping failures noted above remain as carry-forward issues requiring resolution during future consolidation phases of Sprint 6.
