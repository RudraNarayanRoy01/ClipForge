# BATCH 6B.2.2: SUBSYSTEM BOUNDARY & RESPONSIBILITY ANALYSIS

## 1. Purpose
This document provides an architectural analysis of the existing `RuntimeContext` subsystem boundaries, responsibilities, and dependency relationships. It determines which components form genuine architectural boundaries, which are internal implementation collaborators, and how the current architecture functions. This analysis serves as the formal input for subsequent boundary consolidation work in Batch 6B.2.3.

## 2. Scope and Constraints
This is an **ARCHITECTURAL ANALYSIS / DOCUMENTATION ONLY** batch. 
It measures, analyzes, classifies, and recommends. It DOES NOT implement architectural changes, refactor source code, modify existing tests, or alter historical Git records. The repository's executable state remains strictly untouched.

## 3. Evidence Sources
The analysis is based on the inspection of the following repository artifacts and historical anchors:
- **Primary Source:** `backend/src/runtime/core/context.py`
- **Baseline Context:** `backend/docs/certification/BATCH_6B_2_1_RUNTIME_CONTEXT_BASELINE.md`
- **Carry-Forward Context:** `backend/docs/certification/BATCH_6B_1_4_CARRY_FORWARD_BASELINE.md`
- **Closure Record Context:** `backend/docs/certification/BATCH_6B_1_5_FINAL_6A_CLOSURE_RECORD.md`
- **Claim Audit Context:** `backend/docs/certification/BATCH_6B_1_3_CERTIFICATION_CLAIM_AUDIT.md`
- **Historical Context:** `backend/docs/certification/MILESTONE_6A_RECONCILIATION_ADDENDUM.md`

## 4. Evidence Hierarchy
All findings adhere strictly to the established evidence hierarchy:
- **TIER 1 — GIT REALITY:** Commits, SHAs, trees, actual repository state.
- **TIER 2 — REPOSITORY ARTIFACTS:** Actual source code, tests, documentation.
- **TIER 3 — CONTEMPORARY ENGINEERING RECORDS:** Execution plans, specifications.
- **TIER 4 — RETROSPECTIVE INTERPRETATION:** Previous audits, reconciliations.

Architectural findings are explicitly categorized as **FACT** (observable), **DERIVED** (logically derived from facts), **INTERPRETATION** (architectural assessment), **RECOMMENDATION** (forward-looking proposal), or **UNKNOWN** (insufficient evidence).

## 5. RuntimeContext Baseline
Derived directly from the verified Batch 6B.2.1 baseline (**FACT**):
- 0 constructor parameters excluding `self`
- 40 internally instantiated components
- 40 public properties/accessors
- 2 public methods (`register_extension_point`, `get_extension_point`)
- 6 mutable execution-state variables
- 39 import/static fan-out
- 40 construction fan-out
- 40 exposure fan-out
- 0 `RuntimeContext` lifecycle methods
- Explicit cross-subsystem constructor relationships exist
- No established direct concrete provider leakage
- No established direct hardware-specific implementation leakage
- No established application workflow leakage

## 6. Component Classification Method
Components are classified using the following controlled architectural taxonomy (**INTERPRETATION**):
1. **RUNTIME-WIDE CONCERN:** Required across multiple subsystems; appropriate for runtime-level exposure.
2. **SUBSYSTEM ROOT:** A coherent architectural boundary representing a subsystem.
3. **SUBSYSTEM INTERNAL:** Implementation collaborator that should remain hidden behind a boundary.
4. **CROSS-CUTTING SERVICE:** Legitimately consumed across multiple boundaries (e.g., telemetry).
5. **COMPOSITION-ONLY COMPONENT:** Primarily required to construct or wire other components.
6. **STATE HOLDER:** Primary responsibility is runtime or execution state.
7. **ORCHESTRATOR:** Coordinates meaningful execution flows.
8. **LEAF SERVICE:** Focused service with limited architectural responsibility.
9. **UNCERTAIN:** Available evidence is insufficient.

## 7. Complete 40-Component Responsibility Matrix
The following matrix analyzes all 40 instantiated components (**DERIVED / INTERPRETATION / RECOMMENDATION**):

| Component | Current Responsibility | Current Subsystem Group | Dependency Relationships | State Ownership | Lifecycle Relationship | Current RuntimeContext Exposure | Architectural Classification | Recommended Boundary | Evidence Type | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|
| `RuntimeMetadata` | Descriptive data | Metadata | None | Static State | Passive | Property | STATE HOLDER | RETAIN | FACT | HIGH |
| `RuntimeLifecycleCoordinator` | Coordination | Lifecycle | None | Event State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |
| `RuntimeLifecycle` | Exec lifecycle | Lifecycle | None | Event State | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `RuntimeRetry` | Retry evaluation | Resilience | None | Stateless | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `RuntimeObservation` | Observation | Observation | None | Stateless | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `RuntimeCapabilityRegistry` | Arch capabilities | Capability | None | Registry State | Passive | Property | RUNTIME-WIDE CONCERN | EXPOSE | FACT | HIGH |
| `RuntimeResourceDiscovery` | Discovery | Discovery | None | Registry State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |
| `RuntimeProviderRegistry` | Provider catalog | Provider | None | Registry State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | FACT | HIGH |
| `ProviderRegistry` | AI Providers | Provider | None | Registry State | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `ProviderCapabilityRegistry` | AI Capabilities | Provider | None | Registry State | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `ModelRegistry` | Model metadata | Provider | None | Registry State | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `ModelLifecycleManager` | Model states | Provider | None | State | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `ProviderHealthManager` | Health states | Health | None | State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |
| `ProviderFailoverManager` | Failover defs | Resilience | HealthMgr | State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | FACT | HIGH |
| `RuntimeRetryManager` | Retry policies | Resilience | FailoverMgr | State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | FACT | HIGH |
| `RuntimeSchedulingManager`| Eligibility | Scheduling | RetryMgr | State | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `RuntimeExecutionManager` | Exec prep | Execution | SchedMgr | State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | FACT | HIGH |
| `RuntimeHardwareDiscovery`| Hardware info | Discovery | None | State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |
| `RuntimeProviderSelection`| Provider elig | Provider | CapReg, ProvReg, HW | Stateless | Passive | Property | SUBSYSTEM INTERNAL | HIDE | FACT | HIGH |
| `RuntimeScheduler` | Decisions | Scheduling | None | State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |
| `RuntimeExecutionPlanner` | Exec planning | Planning | None | Stateless | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |
| `RuntimeExecutionGraphBuilder`| Graph building | Execution | None | Stateless | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `RuntimeResourceAllocator`| Logical alloc | Resource | None | State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |
| `RuntimeExecutionContextFactory`| Context prep | Execution | None | Stateless | Unknown | Property | COMPOSITION-ONLY COMPONENT | HIDE | DERIVED | HIGH |
| `RuntimeOrchestrator` | Coordination | Execution | None | State | Unknown | Property | ORCHESTRATOR | EXPOSE | FACT | HIGH |
| `AdaptiveRuntime` | Adaptation | Adaptation | None | State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |
| `RuntimeMonitoring` | Observation | Observation | None | State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |
| `RuntimeTelemetry` | Signal capture | Observation | None | State | Unknown | Property | CROSS-CUTTING SERVICE | EXPOSE | DERIVED | HIGH |
| `RuntimeMetrics` | Measurement | Observation | None | State | Unknown | Property | CROSS-CUTTING SERVICE | EXPOSE | DERIVED | HIGH |
| `RuntimeHealth` | Op evaluation | Health | None | State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |
| `RuntimeDiagnostics` | Diag reasoning | Observation | None | Stateless | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `RuntimeOptimization` | Optimization | Adaptation | None | Stateless | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `RuntimeLearning` | Persistence | Adaptation | None | State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |
| `RuntimePlanningStrategy` | Plan philosophy | Planning | None | Stateless | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `RuntimePlanning` | Plan decisions | Planning | None | Stateless | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |
| `RuntimePolicy` | Policy decisions| Planning | None | State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |
| `RuntimeConstraintEngine` | Constraints | Planning | None | Stateless | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `RuntimeBudgetPlanner` | Budgets | Planning | None | State | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `RuntimeRouting` | Routing | Scheduling | None | Stateless | Unknown | Property | SUBSYSTEM INTERNAL | HIDE | DERIVED | HIGH |
| `RuntimeExecutor` | Execution | Execution | None | State | Unknown | Property | SUBSYSTEM ROOT | EXPOSE | DERIVED | HIGH |

## 8. Discovered Subsystem Groups
Based on actual source instantiation and naming conventions, the following groupings logically emerge (**DERIVED**):
- **Provider & Model Management:** Controls catalogs and registries (`RuntimeProviderRegistry`, `ModelRegistry`, `ProviderRegistry`, `ProviderCapabilityRegistry`, `ModelLifecycleManager`).
- **Discovery & Hardware:** Discovers environment capabilities (`RuntimeCapabilityRegistry`, `RuntimeResourceDiscovery`, `RuntimeHardwareDiscovery`).
- **Health, Failover & Resilience:** Manages recovery chains (`ProviderHealthManager`, `ProviderFailoverManager`, `RuntimeRetryManager`, `RuntimeRetry`, `RuntimeHealth`).
- **Execution & Orchestration:** Core execution pathway (`RuntimeExecutionManager`, `RuntimeExecutor`, `RuntimeExecutionContextFactory`, `RuntimeOrchestrator`, `RuntimeExecutionGraphBuilder`).
- **Scheduling & Routing:** Maps workloads (`RuntimeSchedulingManager`, `RuntimeScheduler`, `RuntimeRouting`).
- **Planning & Policy:** Defines boundaries and constraints (`RuntimeExecutionPlanner`, `RuntimePlanning`, `RuntimePlanningStrategy`, `RuntimePolicy`, `RuntimeConstraintEngine`, `RuntimeBudgetPlanner`).
- **Observation & Telemetry:** Monitors signals (`RuntimeObservation`, `RuntimeMonitoring`, `RuntimeTelemetry`, `RuntimeMetrics`, `RuntimeDiagnostics`).
- **Adaptation & Learning:** Adjusts behavior (`AdaptiveRuntime`, `RuntimeOptimization`, `RuntimeLearning`).

## 9. Dependency and Relationship Analysis
The `__init__` method establishes strict constructor relationships.
- **COMPOSITION:** `RuntimeContext` acts as the definitive composition root, owning the construction of all 40 elements.
- **IMPLEMENTATION COLLABORATION:** Many components are currently peers in `RuntimeContext` but conceptually represent an implementation collaboration (e.g., `ProviderFailoverManager` depends on `ProviderHealthManager`).
- **LIFECYCLE:** Operational lifecycle relationships (start, stop) are **NOT ESTABLISHED** in `RuntimeContext`. It acts merely as an instance container.
- **CROSS-CUTTING:** Telemetry and Metrics act as structural cross-cutting dependencies, though their explicit plumbing into other subsystems is not uniformly mandated by the `RuntimeContext` constructor.

## 10. Cross-Subsystem Dependency Analysis
The following cross-subsystem constructor chains exist (**FACT**):
- **Resilience Chain:** `RuntimeSchedulingManager` -> `RuntimeRetryManager` -> `ProviderFailoverManager` -> `ProviderHealthManager`.
- **Selection Chain:** `RuntimeProviderSelection` relies explicitly on `RuntimeCapabilityRegistry`, `RuntimeProviderRegistry`, and `RuntimeHardwareDiscovery`.
- **Execution Chain:** `RuntimeExecutionManager` relies on `RuntimeSchedulingManager`.

These chains represent genuine data flow and policy enforcement pipelines, suggesting that components downstream in the chain (e.g., `ProviderHealthManager`) function as internal dependencies of broader subsystem roots rather than requiring isolated public exposure.

## 11. Exposure Analysis
Currently, 40 properties are exposed directly on `RuntimeContext`.
- **Why is it exposed?** The architecture appears to employ a massive Facade pattern where `RuntimeContext` serves as a singular service catalog.
- **Recommendation:** Only Subsystem Roots and Cross-Cutting Services should be publicly exposed on the context. Internal collaborators (e.g., `ProviderCapabilityRegistry`, `RuntimeExecutionGraphBuilder`, `RuntimeRouting`) should be hidden behind their respective subsystem roots to strengthen encapsulation.

## 12. State Ownership Analysis
`RuntimeContext` currently holds 6 mutable execution state variables (e.g., `active_execution_request`, `active_execution_status`, `active_scheduling_decision`, etc.).
- **What it represents:** Transient execution/request tracking data.
- **Who writes/reads it:** The executing application or orchestrator.
- **Recommendation:** `RuntimeContext` should logically represent the static, structural environment. Mutable execution state should be owned by `RuntimeExecutionContext` or `RuntimeOrchestrator`. Holding active execution state inside the composition root is an architectural anti-pattern for concurrent execution environments.

## 13. Lifecycle Ownership Analysis
- **Construction Owner:** `RuntimeContext` (established).
- **Initialization/Startup Owner:** **NOT ESTABLISHED** by available evidence.
- **Operational Lifecycle Owner:** **NOT ESTABLISHED** by available evidence.
- **Shutdown/Failure Cleanup Owner:** **NOT ESTABLISHED** by available evidence.

## 14. RuntimeContext Architectural Role
- **COMPOSITION ROOT:** **ESTABLISHED**. It hardcodes the construction of 40 objects.
- **SERVICE LOCATOR:** **POTENTIAL SERVICE-LOCATOR CHARACTERISTICS — NOT FULLY ESTABLISHED**. Docstrings and tests use it as one, but deep production usage is not universally verified by repository search.
- **FACADE:** **ESTABLISHED**. It exposes 40 individual subsystems.
- **RUNTIME STATE HOLDER:** **ESTABLISHED**. It holds 6 mutable execution variables.
- **HYBRID:** **ESTABLISHED**. It mixes composition, state holding, and facade responsibilities.
- **TRANSITIONAL ARCHITECTURE:** **POTENTIAL**. The massive fan-out suggests a structure transitioning toward modular boundaries that have not yet been formalized.

## 15. Composition Root Assessment
**CURRENT BENEFITS:**
- Centralized dependency construction.
- Straightforward bootstrap.
- Single unified runtime object.

**CURRENT PRESSURES:**
- **HIGH:** 40 direct constructor calls heavily couples implementation details to the context.
- **HIGH:** Large modification surface. Changing one internal component's constructor breaks `RuntimeContext`.
- **MEDIUM:** Subsystem replacement complexity is high.

## 16. Service Locator / Facade Assessment
The exposure of 40 properties serves as a massive facade. The danger of this pattern is that consumers (whether application workflows or other internal runtime modules) can reach across boundaries and couple directly to low-level implementation details (e.g., accessing `ProviderCapabilityRegistry` directly instead of querying the Provider Subsystem).

## 17. Architectural Pressure Points
1. **Construction Fan-Out:** (Severity: HIGH) 40 dependencies hardcoded in `__init__`.
2. **Exposure Fan-Out:** (Severity: HIGH) 40 properties exposed publicly.
3. **State Concentration:** (Severity: HIGH) Mutable execution state mixed with static composition roots.
4. **Lifecycle Indirection:** (Severity: MEDIUM) Zero explicit lifecycle boundaries managed by the context.

## 18. Architectural Options
**OPTION A — PRESERVE CURRENT RuntimeContext**
Keep all 40 constructors and properties. Retain mutable state.

**OPTION B — GROUPED SUBSYSTEM FACADES**
`RuntimeContext` constructs and exposes 5-7 large grouped facades (e.g., ExecutionFacade, ProviderFacade). All 40 components move behind these facades.

**OPTION C — EXPLICIT RUNTIME SUBSYSTEM REGISTRY**
A formal registry pattern where subsystems register themselves dynamically upon initialization.

**OPTION D — HYBRID (Retain Composition, Restrict Exposure)**
`RuntimeContext` remains the composition root (wiring all 40 components) but changes its exposure. It exposes only 8-10 Subsystem Roots and Cross-Cutting Services. The remaining 30 internal components become private instance variables. Mutable state is migrated to `ExecutionContext`.

## 19. Option Evaluation

| Criterion | Option A (Preserve) | Option B (Grouped Facades) | Option C (Registry) | Option D (Hybrid) |
|---|---|---|---|---|
| Encapsulation | WEAK | STRONG | MODERATE | STRONG |
| Dependency clarity | WEAK | MODERATE | WEAK | STRONG |
| Complexity | LOW | HIGH | HIGH | MODERATE |
| Migration risk | LOW | HIGH | HIGH | LOW |
| Maintainability | WEAK | STRONG | MODERATE | STRONG |

## 20. Recommended Boundary Model
**RECOMMENDATION: OPTION D — HYBRID** (Confidence: HIGH)
- **What remains:** `RuntimeContext` should remain the composition root to preserve centralized wiring and predictable initialization.
- **What changes:** `RuntimeContext` should restrict its public API. It should expose only Subsystem Roots (e.g., `RuntimeOrchestrator`, `RuntimeProviderRegistry`, `RuntimeScheduler`) and Cross-Cutting Services (e.g., `RuntimeTelemetry`).
- **What is hidden:** Internal implementation collaborators (e.g., `ProviderCapabilityRegistry`, `RuntimeExecutionGraphBuilder`) should become private `_internal` properties, effectively enforcing subsystem boundaries by denying public access to them.
- **State migration:** The 6 active execution variables should be removed from `RuntimeContext` and owned by an execution-specific context or orchestrator.

## 21. Migration Principles and Non-Goals
**Migration Principles:**
- Preserve existing provider and hardware abstraction logic.
- Introduce boundaries incrementally by first deprecating properties, then removing them.
- Avoid simultaneous subsystem rewrites.
- Establish robust integration tests before moving execution state ownership.
- Maintain backward compatibility where practical during transition.

**Explicit Non-Goals for this Batch:**
This Batch explicitly DOES NOT:
- Refactor `RuntimeContext`.
- Split `RuntimeContext`.
- Introduce dependency injection frameworks.
- Create new subsystem facades.
- Change lifecycle implementation.
- Move mutable state.
- Change provider adapters or execution scheduling logic.
- Certify runtime completeness or production readiness.

## 22. Batch 6B.2.3 Handoff
This analysis establishes the architectural foundation for implementation work in Batch 6B.2.3.

**Decisions to carry forward:**
1. `RuntimeContext` retains its role as the composition root.
2. The 40 exposed properties must be categorized into Subsystem Roots (to be kept exposed) and Subsystem Internals (to be hidden/made private).
3. Mutable execution state (`active_execution_request`, etc.) must be decoupled from `RuntimeContext`.
4. The historical anchors (`099a33c`, `a76fdef`, `ab07600`, `3cc75a4`, `0fde059d`) remain the definitive historical markers and are not to be re-litigated.

**Unresolved questions for 6B.2.3:**
- Which specific properties currently have deeply embedded test dependencies that will require refactoring when access is restricted?
- What is the exact target object that will receive the 6 mutable state variables?

*This document marks the conclusion of Batch 6B.2.2.*
