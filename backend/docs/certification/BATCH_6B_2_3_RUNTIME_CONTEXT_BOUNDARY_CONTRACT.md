# BATCH 6B.2.3: RUNTIME CONTEXT BOUNDARY CONTRACT

## 1. Purpose
This document provides the definitive, evidence-backed target-state boundary contract for `RuntimeContext`. It translates the analytical findings from Batch 6B.2.1 and Batch 6B.2.2 into a concrete architectural contract. This contract will serve as the strict implementation guide for Batch 6B.2.4.

## 2. Scope and Non-Goals
**Scope:**
- Establish the exact target responsibility of `RuntimeContext`.
- Classify all 40 currently instantiated components into exposure boundaries.
- Define target ownership for the 6 mutable execution-state variables.
- Provide a safe migration and dependency contract for the target architecture.

**Non-Goals:**
- This batch MUST NOT implement the proposed architecture.
- This batch DOES NOT modify the source code, tests, or migrations.
- This batch DOES NOT rewrite Git history.
- This batch DOES NOT introduce new un-evidenced architectural abstractions.

## 3. Evidence Sources
The architectural contract is built strictly upon the following verified repository artifacts:
1. `backend/docs/certification/BATCH_6B_2_1_RUNTIME_CONTEXT_BASELINE.md`
2. `backend/docs/certification/BATCH_6B_2_2_SUBSYSTEM_BOUNDARY_ANALYSIS.md`
3. `backend/docs/certification/BATCH_6B_1_4_CARRY_FORWARD_BASELINE.md`
4. `backend/docs/certification/BATCH_6B_1_5_FINAL_6A_CLOSURE_RECORD.md`
5. `backend/docs/certification/BATCH_6B_1_3_CERTIFICATION_CLAIM_AUDIT.md`
6. `backend/docs/certification/MILESTONE_6A_RECONCILIATION_ADDENDUM.md`
7. `docs/engineering/BATCH_6B_1_1_EVIDENCE_BASELINE.md`
8. `backend/src/runtime/core/context.py`

## 4. Evidence Classification
Findings and instructions are classified as follows:
- **FACT:** Directly observable in source, Git, or an inspected artifact.
- **DERIVED MEASUREMENT:** A conclusion calculated from directly inspected repository evidence.
- **INFERENCE:** An architectural interpretation derived from evidence.
- **RECOMMENDATION:** A proposed target-state decision.
- **UNKNOWN:** Evidence is insufficient to establish the conclusion.

## 5. Current RuntimeContext Responsibility
**FACT:** The current implementation of `RuntimeContext` serves as a massive hybrid object.
- **Composition Root:** It directly constructs 40 subsystems internally.
- **Service Locator / Facade:** It exposes all 40 instantiated components as public properties.
- **State Holder:** It manages 6 mutable active execution-state variables.
- **Lifecycle:** It possesses no explicit initialization or operational lifecycle methods.

## 6. Target RuntimeContext Responsibility
**RECOMMENDATION:** The target boundary contract refines `RuntimeContext` to act purely as a robust Composition Root.
- `RuntimeContext` SHOULD remain responsible for dependency construction, internal dependency wiring, creation of subsystem roots, registration of runtime-wide services, and composition-time configuration.
- `RuntimeContext` SHOULD NOT become responsible for provider-specific execution, scheduling behavior, workload execution, or transient execution-state ownership.

## 7. Boundary Principles
**RECOMMENDATION:** 
1. **Facade Reduction:** `RuntimeContext` must cease to be a universal service catalog.
2. **Subsystem Encapsulation:** Internal implementation collaborators must be hidden behind their respective subsystem roots.
3. **State Relocation:** Transient mutable execution-state must be extracted from the static composition root.
4. **Lifecycle Consistency:** Do not invent new lifecycle behavior; rely on existing lifecycle mechanisms or establish clear boundaries if absent.
5. **Metadata Preservation:** Immutable runtime identity (e.g., `RuntimeMetadata`) is conceptually distinct from mutable execution state and is safely retainable.

## 8. Forty-Component Classification Matrix
**DERIVED MEASUREMENT / RECOMMENDATION:**

| Component | Current Role | Current Subsystem | Target Classification | Target Visibility | Logical Target Owner | Evidence Class | Rationale | Migration Risk |
|---|---|---|---|---|---|---|---|---|
| `RuntimeMetadata` | Descriptive data | Metadata | IMMUTABLE_IDENTITY | PUBLIC | RuntimeContext | FACT | Immutable descriptive identity. | LOW |
| `RuntimeLifecycleCoordinator` | Coordination | Lifecycle | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | Root for lifecycle subsystem. | LOW |
| `RuntimeLifecycle` | Exec lifecycle | Lifecycle | INTERNAL_COLLABORATOR | INTERNAL | RuntimeLifecycleCoordinator | DERIVED | Internal logic for lifecycle. | MEDIUM |
| `RuntimeRetry` | Retry evaluation | Resilience | INTERNAL_COLLABORATOR | INTERNAL | RuntimeRetryManager | DERIVED | Policy execution logic. | MEDIUM |
| `RuntimeObservation` | Observation | Observation | INTERNAL_COLLABORATOR | INTERNAL | RuntimeMonitoring | DERIVED | Leaf observation component. | LOW |
| `RuntimeCapabilityRegistry` | Arch capabilities | Capability | CROSS_CUTTING_SERVICE | PUBLIC | RuntimeContext | FACT | Cross-cutting environment identity. | LOW |
| `RuntimeResourceDiscovery` | Discovery | Discovery | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | Root for capability discovery. | LOW |
| `RuntimeProviderRegistry` | Provider catalog | Provider | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | FACT | Root for global provider catalogs. | LOW |
| `ProviderRegistry` | AI Providers | Provider | INTERNAL_COLLABORATOR | INTERNAL | RuntimeProviderRegistry | DERIVED | Sub-registry. | HIGH |
| `ProviderCapabilityRegistry` | AI Capabilities | Provider | INTERNAL_COLLABORATOR | INTERNAL | RuntimeProviderRegistry | DERIVED | Sub-registry. | HIGH |
| `ModelRegistry` | Model metadata | Provider | INTERNAL_COLLABORATOR | INTERNAL | RuntimeProviderRegistry | DERIVED | Sub-registry. | HIGH |
| `ModelLifecycleManager` | Model states | Provider | INTERNAL_COLLABORATOR | INTERNAL | RuntimeProviderRegistry | DERIVED | Implementation collaborator. | MEDIUM |
| `ProviderHealthManager` | Health states | Health | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | Evaluates provider structures. | LOW |
| `ProviderFailoverManager` | Failover defs | Resilience | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | FACT | Relies on health. | LOW |
| `RuntimeRetryManager` | Retry policies | Resilience | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | FACT | Relies on failover. | LOW |
| `RuntimeSchedulingManager` | Eligibility | Scheduling | INTERNAL_COLLABORATOR | INTERNAL | RuntimeScheduler | DERIVED | Internal routing detail. | HIGH |
| `RuntimeExecutionManager` | Exec prep | Execution | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | FACT | Root execution entry. | LOW |
| `RuntimeHardwareDiscovery` | Hardware info | Discovery | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | Concrete hardware discovery root. | LOW |
| `RuntimeProviderSelection` | Provider elig | Provider | INTERNAL_COLLABORATOR | INTERNAL | RuntimeProviderRegistry/Scheduler | FACT | Depends on internal state. | HIGH |
| `RuntimeScheduler` | Decisions | Scheduling | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | Coordinates routing. | LOW |
| `RuntimeExecutionPlanner` | Exec planning | Planning | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | Coordinates strategy. | LOW |
| `RuntimeExecutionGraphBuilder`| Graph building | Execution | INTERNAL_COLLABORATOR | INTERNAL | RuntimeExecutionManager | DERIVED | Internal graph creation. | MEDIUM |
| `RuntimeResourceAllocator` | Logical alloc | Resource | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | Root allocator. | LOW |
| `RuntimeExecutionContextFactory`| Context prep | Execution | INTERNAL_COLLABORATOR | INTERNAL | RuntimeExecutionManager | DERIVED | Factory builder. | MEDIUM |
| `RuntimeOrchestrator` | Coordination | Execution | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | FACT | Main runtime coordinator. | LOW |
| `AdaptiveRuntime` | Adaptation | Adaptation | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | Adaptive coordinator. | LOW |
| `RuntimeMonitoring` | Observation | Observation | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | Coordinates signals. | LOW |
| `RuntimeTelemetry` | Signal capture | Observation | CROSS_CUTTING_SERVICE | PUBLIC | RuntimeContext | DERIVED | Telemetry is cross-cutting. | LOW |
| `RuntimeMetrics` | Measurement | Observation | CROSS_CUTTING_SERVICE | PUBLIC | RuntimeContext | DERIVED | Metrics are cross-cutting. | LOW |
| `RuntimeHealth` | Op evaluation | Health | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | Evaluates general runtime health. | LOW |
| `RuntimeDiagnostics` | Diag reasoning | Observation | INTERNAL_COLLABORATOR | INTERNAL | RuntimeMonitoring | DERIVED | Internal diagnostic engine. | LOW |
| `RuntimeOptimization` | Optimization | Adaptation | INTERNAL_COLLABORATOR | INTERNAL | AdaptiveRuntime | DERIVED | Internal adaptation engine. | LOW |
| `RuntimeLearning` | Persistence | Adaptation | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | External knowledge persistence. | LOW |
| `RuntimePlanningStrategy` | Plan philosophy | Planning | INTERNAL_COLLABORATOR | INTERNAL | RuntimeExecutionPlanner | DERIVED | Internal strategy detail. | LOW |
| `RuntimePlanning` | Plan decisions | Planning | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | Exposes planning capability. | LOW |
| `RuntimePolicy` | Policy decisions | Planning | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | Exposes policy enforcement. | LOW |
| `RuntimeConstraintEngine` | Constraints | Planning | INTERNAL_COLLABORATOR | INTERNAL | RuntimePlanning | DERIVED | Internal constraint resolution. | LOW |
| `RuntimeBudgetPlanner` | Budgets | Planning | INTERNAL_COLLABORATOR | INTERNAL | RuntimePlanning | DERIVED | Internal planner. | LOW |
| `RuntimeRouting` | Routing | Scheduling | INTERNAL_COLLABORATOR | INTERNAL | RuntimeScheduler | DERIVED | Internal graph routing. | LOW |
| `RuntimeExecutor` | Execution | Execution | SUBSYSTEM_ROOT | PUBLIC | RuntimeContext | DERIVED | Concrete execution wrapper. | LOW |

## 9. Public Exposure Contract
**RECOMMENDATION:** The target `RuntimeContext` will publicly expose ONLY genuine subsystem roots, justified cross-cutting services, and immutable identity descriptors.
- **Genuine Subsystem Roots Exposed:** `RuntimeLifecycleCoordinator`, `RuntimeResourceDiscovery`, `RuntimeProviderRegistry`, `ProviderHealthManager`, `ProviderFailoverManager`, `RuntimeRetryManager`, `RuntimeExecutionManager`, `RuntimeHardwareDiscovery`, `RuntimeScheduler`, `RuntimeExecutionPlanner`, `RuntimeResourceAllocator`, `RuntimeOrchestrator`, `AdaptiveRuntime`, `RuntimeMonitoring`, `RuntimeHealth`, `RuntimeLearning`, `RuntimePlanning`, `RuntimePolicy`, `RuntimeExecutor`.
- **Justified Cross-Cutting Services Exposed:** `RuntimeCapabilityRegistry`, `RuntimeTelemetry`, `RuntimeMetrics`.
- **Immutable Identity Exposed:** `RuntimeMetadata` (Justification: inspection of `backend/src/runtime/core/metadata.py` reveals it is a frozen dataclass intended solely for read-only identity. It does not represent transient execution state, thus it is safe to remain public).
- **Rationale:** Exposing these ensures consumers can reach the formal boundaries of defined subsystems without coupling to their internal mechanisms.

## 10. Internal Collaborator Contract
**RECOMMENDATION:** The target `RuntimeContext` will hide internal implementation collaborators by removing their public property accessors, effectively restricting their access to subsystem roots.
- **Hidden Collaborators:** `RuntimeLifecycle`, `RuntimeRetry`, `RuntimeObservation`, `ProviderRegistry`, `ProviderCapabilityRegistry`, `ModelRegistry`, `ModelLifecycleManager`, `RuntimeSchedulingManager`, `RuntimeProviderSelection`, `RuntimeExecutionGraphBuilder`, `RuntimeExecutionContextFactory`, `RuntimeDiagnostics`, `RuntimeOptimization`, `RuntimePlanningStrategy`, `RuntimeConstraintEngine`, `RuntimeBudgetPlanner`, `RuntimeRouting`.
- **Rationale:** These components represent implementation details (e.g., specific sub-registries, graph builders, routing engines) that conceptually belong behind formal subsystem roots. Exposing them breaks encapsulation and invites dangerous bypass behaviors.

## 11. Test Dependency Analysis
**FACT / DERIVED MEASUREMENT:** Based on repository inspection, properties proposed for internal conversion currently possess dependencies.

| Property | Production References | Test References | Documentation References | Dependency Status | Migration Risk | Required Future Action |
|---|---|---|---|---|---|---|
| `.runtime_lifecycle` | NOT IDENTIFIED IN INSPECTED SEARCH | `test_runtime_context.py` | NOT IDENTIFIED IN INSPECTED SEARCH | IDENTIFIED | LOW | Update test assertions to bypass property. |
| `.runtime_retry` | `runtime_scheduling_manager.py` | `test_runtime_context.py`, `test_runtime_retry_architecture.py` | NOT IDENTIFIED IN INSPECTED SEARCH | IDENTIFIED | MEDIUM | Refactor test assertions; ensure manager passes references internally. |
| `.runtime_observation` | NOT IDENTIFIED IN INSPECTED SEARCH | `test_runtime_context.py`, `test_runtime_intelligence_certification.py` | NOT IDENTIFIED IN INSPECTED SEARCH | IDENTIFIED | LOW | Update test assertions. |
| `.ai_provider_registry` | NOT IDENTIFIED IN INSPECTED SEARCH | `test_provider_registry_architecture.py` | NOT IDENTIFIED IN INSPECTED SEARCH | IDENTIFIED | LOW | Update architecture tests. |
| `.provider_capability_registry` | NOT IDENTIFIED IN INSPECTED SEARCH | `test_provider_capability_architecture.py` | NOT IDENTIFIED IN INSPECTED SEARCH | IDENTIFIED | LOW | Update architecture tests. |
| `.model_registry` | NOT IDENTIFIED IN INSPECTED SEARCH | `test_model_registry_architecture.py` | NOT IDENTIFIED IN INSPECTED SEARCH | IDENTIFIED | LOW | Update architecture tests. |
| `.model_lifecycle_manager` | NOT IDENTIFIED IN INSPECTED SEARCH | `test_model_lifecycle_architecture.py` | NOT IDENTIFIED IN INSPECTED SEARCH | IDENTIFIED | LOW | Update architecture tests. |
| `.runtime_scheduling_manager`| `runtime_execution_manager.py` | `test_runtime_execution_abort_reset.py` | NOT IDENTIFIED IN INSPECTED SEARCH | IDENTIFIED | HIGH | Update test fixtures; ensure internal wiring maintains access. |
| `.provider_selection` | NOT IDENTIFIED IN INSPECTED SEARCH | `test_runtime_selection.py` | NOT IDENTIFIED IN INSPECTED SEARCH | IDENTIFIED | HIGH | Refactor test `context.provider_selection` to use appropriate subsystem. |
| `.execution_graph_builder`| NOT IDENTIFIED IN INSPECTED SEARCH | `test_runtime_graph.py` | NOT IDENTIFIED IN INSPECTED SEARCH | IDENTIFIED | LOW | Update test assertions. |
| `.execution_context_factory`| NOT IDENTIFIED IN INSPECTED SEARCH | `test_execution_context.py` | NOT IDENTIFIED IN INSPECTED SEARCH | IDENTIFIED | LOW | Update test assertions. |
| `.runtime_diagnostics` | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | LOW | Safely remove public property. |
| `.runtime_optimization` | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | LOW | Safely remove public property. |
| `.runtime_planning_strategy`| NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | LOW | Safely remove public property. |
| `.runtime_constraint_engine`| NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | LOW | Safely remove public property. |
| `.runtime_budget_planner` | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | LOW | Safely remove public property. |
| `.runtime_routing` | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | LOW | Safely remove public property. |

*Note: Absence of evidence in the inspected search does not guarantee zero production consumers. Batch 6B.2.4 must handle regressions defensively.*

## 12. Six Mutable State Ownership Analysis
**FACT:** `RuntimeContext` currently holds 6 mutable variables tracking active state.
**RECOMMENDATION:** Composition roots should not manage transient execution state. These variables should be relocated to their appropriate execution or coordination models.

| State Variable | Current Location | Meaning | Writers | Readers | Current Responsibility | Logical Target Owner | Existing Owner? | Evidence Class | Confidence | Migration Risk |
|---|---|---|---|---|---|---|---|---|---|---|
| `active_execution_request` | `RuntimeContext` | Currently executing workload request. | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | Holding state | `RuntimeExecutionContext` | YES | DERIVED | HIGH | MEDIUM |
| `active_execution_status` | `RuntimeContext` | Track runtime status of execution. | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | Holding state | `RuntimeExecutionContext` | YES | DERIVED | HIGH | MEDIUM |
| `active_scheduling_decision` | `RuntimeContext` | Track latest routing decision. | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | Holding state | `RuntimeScheduler` | YES | DERIVED | HIGH | MEDIUM |
| `active_lifecycle_result` | `RuntimeContext` | Track execution lifecycle step. | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | Holding state | `RuntimeLifecycleCoordinator` | YES | DERIVED | HIGH | MEDIUM |
| `active_retry_result` | `RuntimeContext` | Track retry state/outcomes. | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | Holding state | `RuntimeRetryManager` | YES | DERIVED | HIGH | MEDIUM |
| `active_observation_result`| `RuntimeContext` | Track emitted observations. | NOT IDENTIFIED IN INSPECTED SEARCH | NOT IDENTIFIED IN INSPECTED SEARCH | Holding state | `RuntimeMonitoring` | YES | DERIVED | HIGH | MEDIUM |

*Note: An exhaustive codebase search returned no external writers or readers for these exact attributes on `RuntimeContext`. They appear to be historically held definitions. `RuntimeExecutionContext` is confirmed to exist as an established entity (`src/runtime/execution/runtime_execution_context.py`) and is the logical recommended target owner for the execution request/status variables. The target owners are recommended, not currently implemented.*

## 13. Lifecycle Boundary Contract
**FACT:** The current `RuntimeContext` owns construction but lacks operational lifecycle methods (`start`, `stop`, `initialize`). Inspections show `RuntimeBootstrap` handles initialization, and `RuntimeLifecycleCoordinator` manages structural lifecycle logic.
**RECOMMENDATION:**
- **Construction Ownership:** `RuntimeContext` REMAINS the construction owner.
- **Operational Lifecycle Ownership:** `RuntimeContext` MUST NOT adopt new operational lifecycle logic. The architecture must continue to rely on the existing mechanisms (`RuntimeBootstrap` for composition phase, `RuntimeLifecycleCoordinator` for execution phase) to coordinate the lifecycle.
- **Contract:** Do not introduce `.initialize()` or `.start()` methods into `RuntimeContext` during implementation.

## 14. Target Subsystem Root Model
**INFERENCE / RECOMMENDATION:** The targeted architecture recognizes the following logical boundaries (enforced by the public exposure contract):
- **Provider & Model Management Root:** `RuntimeProviderRegistry`
- **Discovery & Hardware Root:** `RuntimeHardwareDiscovery`, `RuntimeResourceDiscovery`
- **Health, Failover & Resilience Roots:** `ProviderHealthManager`, `ProviderFailoverManager`, `RuntimeRetryManager`, `RuntimeHealth`
- **Execution & Orchestration Roots:** `RuntimeExecutionManager`, `RuntimeOrchestrator`, `RuntimeExecutor`
- **Scheduling & Routing Root:** `RuntimeScheduler`
- **Planning & Policy Roots:** `RuntimeExecutionPlanner`, `RuntimePlanning`, `RuntimePolicy`
- **Observation & Telemetry Roots:** `RuntimeMonitoring`
- **Adaptation & Learning Roots:** `AdaptiveRuntime`, `RuntimeLearning`

## 15. Cross-Cutting Service Contract
**RECOMMENDATION:** The following components are explicitly identified as legitimate cross-cutting services and are permitted to remain exposed globally via `RuntimeContext`:
- `RuntimeTelemetry`
- `RuntimeMetrics`
- `RuntimeCapabilityRegistry`

These services are necessary across all subsystem boundaries and hiding them would result in severe dependency duplication. (Note: `RuntimeMetadata` is also exposed, but specifically as an immutable descriptor, not an active service).

## 16. Provider and Hardware Abstraction Invariants
**RECOMMENDATION (INVARIANT):**
- The target boundary contract MUST preserve existing provider abstraction. `RuntimeContext` must not directly reference Ollama, Gemini, OpenAI, or vendor-specific capabilities.
- The target boundary contract MUST preserve existing hardware abstraction. `RuntimeContext` must not directly reference CUDA, VRAM limits, or CPU/GPU logic.
- Concrete knowledge remains completely encapsulated behind `RuntimeProviderRegistry` and `RuntimeHardwareDiscovery`.

## 17. Option D — Hybrid Target Architecture
**RECOMMENDATION:** Batch 6B.2.2 Option D is hereby ratified as the implementation target.
- **KEEP:** `RuntimeContext` as the central, statically wired composition root.
- **EXPOSE:** Only genuine subsystem roots and justified cross-cutting services.
- **HIDE:** Internal implementation collaborators.
- **RELOCATE:** Transient mutable execution state to their appropriate logical architectural owners.
- **PRESERVE:** Provider and hardware abstraction.
- **DELEGATE:** Operational lifecycle to existing appropriate external mechanisms.

## 18. Batch 6B.2.4 Implementation Contract
Batch 6B.2.4 must implement this exact contract.

**Implementation Directives:**
A. **Files to Modify:** `backend/src/runtime/core/context.py` and strictly related unit/architecture tests.
B. **Visibility Changes:** Remove public exposure of components designated as `INTERNAL_COLLABORATOR` while preserving required internal access. Use safe implementation mechanics (e.g., private attributes or constructor wiring) as dictated by evidence.
C. **Properties to Remain Public:** All designated `SUBSYSTEM_ROOT`, `CROSS_CUTTING_SERVICE`, and `IMMUTABLE_IDENTITY` properties.
D. **State Migration:** Move the 6 mutable variables out of `RuntimeContext`. Migrate them to their recommended target owners (e.g., `RuntimeExecutionContext`), adjusting test dependencies dynamically.
E. **Lifecycle Unchanged:** Do not add start/stop logic to `context.py`.
F. **Forbidden Shortcuts:** Do not create a new god-object `ExecutionManager` to just wrap the hidden properties. Do not rewrite test logic beyond adapting to the hidden properties.

## 19. Migration Risks and Constraints
**MANDATORY RULES FOR BATCH 6B.2.4:**
- **RULE 1:** Do not blindly delete `RuntimeContext` properties without redirecting test fixtures.
- **RULE 2:** Do not break existing scheduling/retry/failover behavior to achieve cleanliness.
- **RULE 3:** Do not replace one giant facade with another giant facade.
- **RULE 4:** Do not introduce speculative abstractions (e.g., Dependency Injection containers).
- **RULE 5:** Do not introduce provider-specific or hardware-specific logic into `RuntimeContext`.
- **RULE 6:** Every state migration must have an explicit target owner.
- **RULE 7:** Test dependencies must be deliberately migrated rather than ignored.
- **RULE 8:** Lifecycle behavior must remain semantically equivalent.
- **RULE 9:** Do not modify unrelated runtime subsystems while implementing the boundary.
- **RULE 10:** Do not claim architectural completion merely because the API surface becomes smaller.

## 20. Acceptance Criteria and Handoff
This boundary contract serves as the ultimate design artifact for the RuntimeContext consolidation.

**Handoff to 6B.2.4:**
The architectural analysis phase for Milestone 6B.2 is concluded. Batch 6B.2.4 is authorized to proceed with the source code modifications explicitly outlined in Sections 8, 9, 10, 12, and 18, strictly adhering to the invariants in Sections 16 and 19.
