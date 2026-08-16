# Batch 6B.2.1: RuntimeContext Architectural Measurement & Baseline

## 1. Purpose
This document establishes an objective, repository-grounded baseline of the CURRENT `RuntimeContext` architecture before any composition refactoring occurs in Sprint 6B.2. It measures what `RuntimeContext` actually owns, constructs, exposes, depends upon, and connects.

## 2. Batch / Repository Identity
- **Milestone:** 6B — Final Platform Integrity & Runtime Consolidation
- **Sprint:** 6B.2 — Runtime Composition Consolidation
- **Batch:** 6B.2.1 (RuntimeContext Architectural Measurement & Baseline)
- **Branch:** main
- **HEAD (Full):** 10d7e00ada78a0bb9e050ecfb944d237dfd11263
- **HEAD (Short):** 10d7e00
- **Measurement Timestamp:** 2026-08-16T22:15:37+05:30
- **Previous Batch Identity:** 06847f2 (Batch 6B.1.4 establish carry-forward baseline)

## 3. RuntimeContext Source Location
- **Authoritative Implementation:** `backend/src/runtime/core/context.py`
- **Class Definition:** `class RuntimeContext:` (Line 50)

## 4. Measurement Methodology
Measurements were derived via direct repository inspection. Only active codebase artifacts were counted. Relationships were traced by inspecting `__init__` signatures, object instantiation logic, and import statements.

## 5. Constructor Dependency Baseline
- **Constructor Signature:** `def __init__(self) -> None:`
- **Total Constructor Parameters:** 0 (excluding `self`)
- **Typed Dependencies (Injected externally):** 0
- **Configuration/Value Parameters:** 0
- **Internally Instantiated Dependencies:** 40
- **Optional Dependencies:** 0

`RuntimeContext` does not accept any dependencies via its constructor. It operates entirely via internal instantiation.

## 6. Directly Instantiated Components
`RuntimeContext` directly constructs the following 40 subsystems/components. For all listed components:
- **Directly constructed?** YES
- **Lifecycle ownership?** INSTANCE-LIFETIME BOUND; OPERATIONAL LIFECYCLE OWNERSHIP NOT ESTABLISHED
- **Composition responsibility?** YES (Constructed and wired by `RuntimeContext`)

Components:
1. `RuntimeMetadata`
2. `RuntimeLifecycleCoordinator`
3. `RuntimeLifecycle`
4. `RuntimeRetry`
5. `RuntimeObservation`
6. `RuntimeCapabilityRegistry`
7. `RuntimeResourceDiscovery`
8. `RuntimeProviderRegistry`
9. `ProviderRegistry`
10. `ProviderCapabilityRegistry`
11. `ModelRegistry`
12. `ModelLifecycleManager`
13. `ProviderHealthManager`
14. `ProviderFailoverManager` (injected with `ProviderHealthManager`)
15. `RuntimeRetryManager` (injected with `ProviderFailoverManager`)
16. `RuntimeSchedulingManager` (injected with `RuntimeRetryManager`)
17. `RuntimeExecutionManager` (injected with `RuntimeSchedulingManager`)
18. `RuntimeHardwareDiscovery`
19. `RuntimeProviderSelection` (injected with capabilities, providers, hardware)
20. `RuntimeScheduler`
21. `RuntimeExecutionPlanner`
22. `RuntimeExecutionGraphBuilder`
23. `RuntimeResourceAllocator`
24. `RuntimeExecutionContextFactory`
25. `RuntimeOrchestrator`
26. `AdaptiveRuntime`
27. `RuntimeMonitoring`
28. `RuntimeTelemetry`
29. `RuntimeMetrics`
30. `RuntimeHealth`
31. `RuntimeDiagnostics`
32. `RuntimeOptimization`
33. `RuntimeLearning`
34. `RuntimePlanningStrategy`
35. `RuntimePlanning`
36. `RuntimePolicy`
37. `RuntimeConstraintEngine`
38. `RuntimeBudgetPlanner`
39. `RuntimeRouting`
40. `RuntimeExecutor`

## 7. Public API Baseline
- **Public Properties/Accessors:** 40 properties exposing the instantiated subsystems.
- **Public Methods:** 2 methods (`register_extension_point`, `get_extension_point`).
- **Public State Attributes:** 6 mutable fields tracking active execution state.
- **Lifecycle Operations:** 0 (No `start()`, `stop()`, or `initialize()` methods on the context itself).

## 8. Internal State Baseline
- **Configuration:** None.
- **Caches/Registries:** `_extension_points` (Dictionary).
- **Subsystem References:** 40 private variables (e.g., `_scheduler`, `_orchestrator`).
- **Execution State (Mutable):**
  - `active_execution_request`
  - `active_execution_status`
  - `active_scheduling_decision`
  - `active_lifecycle_result`
  - `active_retry_result`
  - `active_observation_result`

## 9. Fan-Out Analysis
- **Static / Import Fan-Out:** 39 direct module imports from within `src.runtime.core`.
- **Construction / Composition Fan-Out:** 40 internally constructed dependencies.
- **Public API / Exposure Fan-Out:** 40 strictly typed return values from properties.

## 10. Fan-In Analysis
- **Production Fan-In:** Direct production references identified by the repository search are concentrated in `RuntimeBootstrap` (which instantiates and exposes `RuntimeContext`). Additional runtime consumption could not be established exhaustively from the inspected references and remains an open question. Numerous docstring references advise subsystems to locate dependencies via `RuntimeContext`.
- **Test Fan-In:** Extensively consumed by test fixtures and certification tests (e.g., `test_runtime_architecture_certification.py`, `test_runtime_context.py`, etc.).
- **Tooling/Documentation Fan-In:** Used heavily in documentation and architectural compliance scripts.

## 11. Cross-Subsystem Dependency Analysis
`RuntimeContext` wires several cross-subsystem dependencies during instantiation:

| Subsystem | Component | Dependency | Classification |
|---|---|---|---|
| Health | `ProviderFailoverManager` | `ProviderHealthManager` | Direct constructor injection |
| Resilience | `RuntimeRetryManager` | `ProviderFailoverManager` | Direct constructor injection |
| Scheduling | `RuntimeSchedulingManager` | `RuntimeRetryManager` | Direct constructor injection |
| Execution | `RuntimeExecutionManager` | `RuntimeSchedulingManager` | Direct constructor injection |
| Provider/Resource | `RuntimeProviderSelection` | `RuntimeCapabilityRegistry`, `RuntimeProviderRegistry`, `RuntimeHardwareDiscovery` | Direct constructor injection |

All other subsystems are constructed in isolation and merely exposed side-by-side.

## 12. Provider Leakage Analysis
Does `RuntimeContext` directly depend on concrete provider knowledge?
- **Result:** NOT FOUND.
- **Evidence:** Instantiates `ProviderRegistry` and `ModelRegistry`, but does not mention or import specific implementations (e.g., OpenAI, AWS).

## 13. Hardware / Resource Leakage Analysis
Does `RuntimeContext` directly know about hardware-specific implementation details?
- **Result:** NOT FOUND.
- **Evidence:** Instantiates `RuntimeHardwareDiscovery`, but contains no CUDA, VRAM, or CPU-specific logic or strings.

## 14. Application Leakage Analysis
Does `RuntimeContext` directly know about application-level concerns?
- **Result:** NOT FOUND.
- **Evidence:** No mentions of campaigns, clips, HTTP APIs, or frontend workflows. It is strictly limited to generic runtime orchestration concepts.

## 15. Lifecycle Responsibility Analysis
| Operation | RuntimeContext owns it? | Delegates it? | Merely exposes it? | Evidence |
|---|---|---|---|---|
| initialize | NO | NO | NO | No initialization method exists |
| start | NO | NO | NO | No start method exists |
| stop | NO | NO | NO | No stop method exists |
| shutdown | NO | NO | NO | No shutdown method exists |
| cleanup | NO | NO | NO | No cleanup method exists |
| reset | NO | NO | NO | No reset method exists |

**Evidence:** `RuntimeContext` has zero lifecycle methods. It acts as a passive container.

## 16. Composition Responsibility Analysis
| Role | Classification | Evidence |
|---|---|---|
| Composition Root | PRESENT | Constructs 40 dependencies internally. |
| Dependency Container | PARTIAL | Holds subsystem references and extension points, but lacks generic dependency resolution APIs. |
| Service Locator | PRESENT | Exposes properties for downstream components to fetch subsystems. |
| Bootstrapper | NOT EVIDENCED | Instantiated by `RuntimeBootstrap`. |
| Factory | NOT EVIDENCED | (Except for returning a previously constructed `execution_context_factory`). |
| Dependency Registry | PARTIAL | Registers extension points, but statically holds core subsystems. |
| Subsystem Assembler | PRESENT | Wires inter-manager dependencies (e.g., `RuntimeProviderSelection`). |
| Lifecycle Coordinator | NOT EVIDENCED | Contains no lifecycle logic. |
| Facade | PRESENT | Provides a single unified surface for 40 subsystems. |
| Runtime State Holder | PRESENT | Contains 6 mutable execution state variables. |

## 17. Consolidated Responsibility Matrix
| Responsibility | Present? | Current owner | Evidence | Confidence | Architectural observation |
|---|---|---|---|---|---|
| Runtime construction | YES | `RuntimeContext` | Constructs 40 core subsystems | DIRECT | Hardcoded internal construction |
| Dependency registration | PARTIAL | `RuntimeContext` | `register_extension_point` | DIRECT | Limited to extensions only |
| Dependency exposure | YES | `RuntimeContext` | 40 property accessors | DIRECT | Massive public API surface |
| Lifecycle initialization | NO | UNKNOWN | No init methods | DIRECT | Passive object |
| Provider access | YES | `RuntimeContext` | `provider_registry` property | DIRECT | Acts as facade |
| Resource/hardware access | YES | `RuntimeContext` | `hardware_discovery` property | DIRECT | Acts as facade |
| Execution access | YES | `RuntimeContext` | `executor` property | DIRECT | Acts as facade |
| Application orchestration | NO | UNKNOWN | No application logic | DIRECT | Pure infrastructure focus |

## 18. Evidence Confidence / Unknowns
- **Confidence:** HIGH. All measurements are derived directly from source inspection of `context.py`.
- **Unknowns:** How extensively downstream components actually use the exposed properties at runtime, as most fan-in evidence is in tests or docstrings.

## 19. Architectural Observations
- **High Construction Fan-Out:** Instantiating 40 internal dependencies directly couples `RuntimeContext` to the constructor signatures of every subsystem. This indicates composition concentration but does not by itself establish that the current architecture is incorrect.
- **Broad Subsystem Exposure:** The class exposes 40 individual subsystems as properties, creating a massive facade surface. This relationship warrants boundary analysis in 6B.2.2.
- **State Holding:** The presence of mutable active execution state variables inside a composition root mixes execution tracking with composition.

## 20. Explicit Non-Conclusions
This baseline measurement DOES NOT establish that:
- `RuntimeContext` must be deleted or split.
- `RuntimeContext` must become a thin facade.
- Dependency injection or a DI container is required.
- A new composition root is required.
- Bootstrap must be rewritten.
- High fan-out automatically means bad architecture.
- Public exposure automatically means architectural leakage.

## 21. Handoff to Batch 6B.2.2
**ESTABLISHED FACTS:**
- `RuntimeContext` statically constructs 40 subsystems.
- `RuntimeContext` provides 40 property accessors, acting as a massive facade.
- `RuntimeContext` is strictly passive and contains zero lifecycle coordination or execution logic itself.

**ARCHITECTURAL PRESSURE POINTS:**
- The coupling of 40 constructors inside a single `__init__` method.
- The hosting of active execution state inside a composition class.

**UNKNOWN / UNRESOLVED QUESTIONS:**
- Are all 40 subsystems genuinely required to be global within the runtime environment, or are some internal implementation details?

**QUESTIONS FOR 6B.2.2:**
Which measured `RuntimeContext` relationships represent genuine subsystem boundaries, and which are legitimate cross-cutting composition concerns?
