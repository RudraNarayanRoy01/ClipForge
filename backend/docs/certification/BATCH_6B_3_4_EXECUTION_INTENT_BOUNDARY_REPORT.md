# BATCH 6B.3.4 EXECUTION INTENT BOUNDARY REPORT

## 1. Batch Objective
The objective of Batch 6B.3.4 was to establish the smallest correct Runtime-level declarative boundary representing: "This capability has been resolved, and this is the work that the Runtime may eventually execute." The new abstraction, `ExecutionIntent`, serves as a strict boundary separating capability resolution from future execution planning, provider selection, and scheduling.

## 2. Existing Abstractions Investigated
A repository-wide discovery inspected abstractions including `ExecutionRequest`, `RuntimeExecutionRequest`, `ExecutionIntent`, `RuntimeExecutionIntent`, `AIRequest`, `ExecutionPlan`, and `ExecutionResult`.

## 3. Rejected Alternatives
- **`runtime/core/execution_model.py::ExecutionRequest`**: Rejected because it already incorporates downstream concepts such as `planning_decision` and `policy_decision`. Reusing it would collapse the planning boundary into the intent boundary.
- **`reasoning/execution/models.py::ExecutionRequest`**: Rejected because it is domain-specific (contains `campaign_id`, `media_asset_id`) and is not provider-neutral.
- **`AIRequest`**: Rejected because it belongs to the intelligence layer and lacks a capability identity binding.

## 4. CREATE Decision
**Decision: OPTION C — CREATE**
Based on the inspected repository, no existing abstraction correctly represents a planning-neutral, provider-neutral, and hardware-neutral declarative boundary. A new `ExecutionIntent` model was created.

## 5. ExecutionIntent Contract
```python
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ExecutionIntent:
    capability_id: str
    payload: Any
    output_contract: str | None = None
```

## 6. Field Semantics
- **`capability_id` (str)**: WHAT capability is being requested. It remains provider-neutral and does not encode hardware or endpoints.
- **`payload` (Any)**: WHAT input/work data accompanies the request.
- **`output_contract` (str | None)**: WHAT result shape the caller expects.

## 7. Payload Typing Decision
The `payload` is intentionally opaque (`Any`) at this boundary because no existing Runtime-core, provider-neutral payload contract was identified that is suitable for this abstraction. The object is structurally immutable, though recursive immutability of arbitrary payload contents is not provided.

## 8. Output-Contract Semantics
The `output_contract` is a descriptive identifier (e.g., `"ExtractionSummarySchema"`). Within the inspected scope, it does NOT register, instantiate, or validate schemas.

## 9. Provider Neutrality
The current implementation contains no dependency on concrete providers. `ExecutionIntent` does not require Ollama, OpenAI, Gemini, or any provider configuration.

## 10. Hardware Neutrality
The current implementation contains no dependency on hardware discovery or execution. It does not require GPU, CUDA, or RAM specifics.

## 11. Execution Neutrality
The intent model is a passive declarative value object. It does not import or invoke `RuntimeExecutor`, produce `RuntimeExecutionResult`, schedule work, or perform network requests.

## 12. Planning Neutrality
The selected boundary does not incorporate `planning_decision`, `execution_strategy`, `provider_selection`, or other scheduling/policy decisions.

## 13. Application Separation
The application's AI execution path remains unchanged. `ExecutionIntent` does not integrate with `CampaignIntelligenceService` or application DI wiring.

## 14. Sprint 6B.2 Invariant Preservation
The `RuntimeContext` 23 PUBLIC / 17 INTERNAL boundary remains untouched. `RuntimeExecutionContext` remains a frozen two-field dataclass. Hardware and provider abstractions remain unchanged.

## 15. Unit-Test Coverage
Focused tests in `test_intent.py` cover:
- Construction with valid fields
- `capability_id` preservation
- Payload preservation (opaque)
- `output_contract` preservation
- Structural immutability (`FrozenInstanceError`)
- Provider, Hardware, and Execution neutrality

## 16. Architecture-Test Coverage
`test_intent_architecture.py` utilizes AST inspection to verify that `intent.py` does not import concrete providers, provider factories, hardware modules, executor modules, scheduler modules, or application intelligence services.

## 17. Verification Results
- **Unit Tests**: 8 passed (intent tests).
- **Architecture Tests**: 48 passed.
- **Runtime Regression Tests**: The executed runtime regression suite produced 51 passed tests, 3 pre-existing carry-forward failures, and 26 warnings.
- **Git diff**: Clean (`--check` passed, no modified tracked files).

## 18. Current vs Target State
**CURRENT**: Application AI execution bypasses Runtime entirely. `CapabilityRequest` and `CapabilityResolver` exist purely as knowledge-resolution mechanisms. `ExecutionIntent` establishes the declarative request boundary.
**TARGET (FUTURE)**: The application will eventually route requests through `CapabilityResolver` -> `ExecutionIntent` -> `ExecutionPlanner` -> `RuntimeExecutor`.

## 19. Known Carry-Forward Defects
The 3 failures in `pytest backend/tests/runtime/` are verified pre-existing defects from prior batches and were not caused by Batch 6B.3.4:
- `test_one_component_one_artifact_mapping`
- `test_decision_ownership_mapping`
- `test_pipeline_completeness_and_uniqueness`

## 20. Explicit Non-Goals
This Batch does NOT:
- Execute capabilities
- Select providers or models
- Allocate hardware resources
- Build an execution scheduler
- Introduce a recursive immutability framework
- Build a generic payload serialization system

## 21. Batch 6B.3.5 Handoff
Batch 6B.3.5 may consume `CapabilityRequest`, `CapabilityResolver`, `CapabilityDescriptor`, and `ExecutionIntent`. It MUST NOT assume provider selection, scheduling, or actual execution already exists.
