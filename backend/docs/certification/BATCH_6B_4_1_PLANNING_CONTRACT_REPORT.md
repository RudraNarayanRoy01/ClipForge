# BATCH 6B.4.1 PLANNING CONTRACT CERTIFICATION REPORT

## 1. Batch Identity
- **Milestone:** 6B — Runtime Capability & Planning Foundation
- **Sprint:** 6B.4 — Planning Boundary
- **Batch:** 6B.4.1 — Planning Contract & Decision Model

## 2. Purpose
Establish ONE authoritative Runtime-core value object representing HOW the Runtime intends to satisfy an `ExecutionIntent`. This establishes the architectural boundary between declarative intent and future planning/policy systems.

## 3. Repository Baseline
- **Branch:** main
- **HEAD:** 499064122c5f43e2bc9090c61292d2ff205b97b9
- **Short HEAD:** 4990641

## 4. Existing Abstraction Discovery
A repository-wide discovery revealed the following:
- `ExecutionPlan` in `planner.py`
- `ExecutionPlan` in `runtime/execution/`
- `PlanningDecision` in `runtime_planning.py`

## 5. Why Existing ExecutionPlan Abstractions Were Rejected
- The `ExecutionPlan` in `planner.py` is downstream-oriented and consumes a `SchedulingDecision`, which violates the `Intent -> Plan -> Schedule` architectural pipeline.
- The `ExecutionPlan` in `runtime/execution/` is tightly coupled to the Execution Engine and does not cleanly represent the planning boundary.

## 6. Why Existing PlanningDecision Was Rejected
- The `PlanningDecision` in `runtime_planning.py` answers generic adaptive-runtime questions (e.g., "What should happen next?") rather than "How do we satisfy this specific ExecutionIntent?" It handles different architectural responsibilities.

## 7. CREATE Decision
Due to the unsuitability of existing models, the decision was to CREATE a single authoritative contract. `PlanningResult` was selected as the concept.

## 8. Exact PlanningResult Contract
```python
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from .intent import ExecutionIntent

@dataclass(frozen=True)
class PlanningResult:
    intent: ExecutionIntent
    strategy: str
    requirements: Tuple[str, ...] = field(default_factory=tuple)
    constraints: Dict[str, Any] = field(default_factory=dict)
```

## 9. Field-by-Field Semantics
- **`intent`**: The exact declarative `ExecutionIntent`. Preserves traceability between WHAT is requested and HOW it is planned. Does not mutate the intent.
- **`strategy`**: A provider-neutral, hardware-neutral string defining the abstract approach (e.g., "local", "remote").
- **`requirements`**: An immutable `Tuple[str, ...]` defining declarative requirements. Not a hardware/provider configuration.
- **`constraints`**: A `Dict[str, Any]` defining declarative limits/constraints. Does not interpret, enforce, or hold scheduler state.

## 10. Explicit Exclusion of planning_provenance
`planning_provenance` was explicitly excluded to prevent the foundational contract from becoming a dumping ground for policy state, telemetry, and diagnostics.

## 11. Immutability Semantics
`PlanningResult` uses `@dataclass(frozen=True)` for structural/top-level immutability. Nested collections (like `constraints`) are not deeply frozen. Tests correctly verify that direct field reassignment is rejected.

## 12. Provider Neutrality
Verified by `test_planning_result_architecture.py`. No provider implementations or factories (e.g., Ollama, OpenAI, Gemini) are imported or referenced.

## 13. Hardware Neutrality
Verified by `test_planning_result_architecture.py`. No hardware concepts (e.g., GPU, CUDA, VRAM) are imported or referenced.

## 14. Scheduling Neutrality
Verified by `test_planning_result_architecture.py`. No scheduling or queue concepts are imported.

## 15. Execution Neutrality
Verified by `test_planning_result_architecture.py`. No execution engine or execution lifecycle methods (`execute`, `run`) exist.

## 16. Application Separation
Verified by `test_planning_result_architecture.py`. No domain schemas, Pydantic models, or FastAPI services are referenced.

## 17. Test Results
- **Unit & Architecture Tests (`backend/tests/unit/runtime/core/test_planning_result.py`, `backend/tests/architecture/runtime/test_planning_result_architecture.py`):** 9 tests passed.
- **Full Architecture Tests (`backend/tests/architecture/runtime/`):** 55 passed.
- **Full Runtime Tests (`backend/tests/runtime/`):** 51 passed, 3 failed.

## 18. Pre-existing Failures
The following failures occurred in `pytest backend/tests/runtime/`:
1. `FAILED backend/tests/runtime/test_runtime_architecture_certification.py::test_one_component_one_artifact_mapping`
2. `FAILED backend/tests/runtime/test_runtime_governance_certification.py::TestOwnershipRules::test_decision_ownership_mapping`
3. `FAILED backend/tests/runtime/test_runtime_pipeline_certification.py::TestRuntimePipelineCertification::test_pipeline_completeness_and_uniqueness`

These are known carry-forward issues resulting from existing architecture tests expecting a complete mapping. Per instructions, these were deliberately left unpatched to respect the change budget.

## 19. Exact Change Set
- **4 NEW FILES:**
  - `backend/src/runtime/core/planning_result.py`
  - `backend/tests/unit/runtime/core/test_planning_result.py`
  - `backend/tests/architecture/runtime/test_planning_result_architecture.py`
  - `backend/docs/certification/BATCH_6B_4_1_PLANNING_CONTRACT_REPORT.md`
- **0 MODIFIED FILES.**

## 20. Git Integrity
No history rewrites, commits, or tags were created during implementation. The baseline commit remains `499064122c5f43e2bc9090c61292d2ff205b97b9`.

## 21. Current-vs-Target State
- **CURRENT:** `ExecutionIntent` represents WHAT is requested. The Runtime now has an authoritative contract (`PlanningResult`) representing HOW it will be satisfied.
- **REMAINS FUTURE WORK:** The Planner implementation, Policy Engine, Provider Selection, Hardware Selection, Scheduler, and Execution logic are NOT PRESENT.

## 22. 6B.4.2 Handoff
- **6B.4.2 may consume:** `ExecutionIntent`, `ExecutionIntentValidator`, and `PlanningResult`.
- **6B.4.2 MUST NOT assume:** That a Planner, Policy Engine, Provider/Hardware Selection, Scheduler, or Execution currently exists.
