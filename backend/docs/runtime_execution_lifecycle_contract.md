# Runtime Execution Lifecycle Contract

## 1. Purpose

The purpose of this contract is to establish the canonical architectural boundaries, states, outcomes, and transitions of the Runtime Execution Lifecycle. This document formally dictates "what the lifecycle means" structurally for the current verified 6C execution architecture.

## 2. Component Boundaries and Ownership Matrix

The execution lifecycle explicitly isolates workload normalization, mechanism resolution, execution dispatch, and terminalization into distinct concepts owned by distinct components.

| Concern | Owner |
|---------|-------|
| Workload normalization | `RuntimeExecutionBoundary` |
| Execution admission | `RuntimeExecutionBoundary` (yields `ExecutionAdmission`) |
| Mechanism resolution | `ExecutionEngine` (via `ExecutionMechanismRegistry`) |
| Execution attempt | `Concrete Execution Mechanism` |
| Provider invocation | `Concrete Execution Mechanism` |
| Terminal execution record | `ExecutionResult` |
| Terminal outcome taxonomy | `ExecutionOutcome` |

### 2.1. Boundary Responsibility
`RuntimeExecutionBoundary` is strictly an entry boundary. It normalizes an `ExecutionIntent` into an `ExecutionAdmission` to ensure that execution requests are structurally valid before they reach the engine. It does **not** perform execution itself.

### 2.2. Engine Responsibility
`ExecutionEngine` is the authoritative orchestrator for the runtime domain. It takes the `ExecutionAdmission`, resolves the appropriate mechanism via the `ExecutionMechanismRegistry`, and delegates the execution attempt to the concrete mechanism. It constructs the final `ExecutionResult`. 

### 2.3. Mechanism Responsibility
A concrete `ExecutionMechanism` (e.g., `WhisperExecutionMechanism`) owns the actual execution attempt, provider invocation, and translation of provider-specific exceptions. It defines the mapping to `ExecutionOutcome` based on the success or failure of the execution attempt, returning it to the engine.

### 2.4. Result Responsibility
`ExecutionResult` is an immutable, terminal record of an actual execution attempt. It contains the `target`, the `outcome`, and an `error_message` if applicable.

### 2.5. Outcome Taxonomy
`ExecutionOutcome` represents the historical, terminal fact evaluated during the attempt. It contains exactly:
- `SUCCESS`
- `FAILED`
- `REJECTED`
- `CANCELLED`

---

## 3. Historical Note: Legacy Execution Lifecycle (Sprint 6B)

> **Important**: The components, lifecycle states, and transition engines documented below (`RuntimeExecutionSession`, `RuntimeExecutionCoordinator`, `RuntimeExecutor`, `RuntimeExecutionResult`, `RuntimeExecutionLifecycleState`) represent the multi-stage 6B architectural design. They are **not part of the current production execution path** and have been superseded by the `ExecutionEngine` orchestrator model detailed in Section 2. They are preserved here strictly as historical architectural context.

### 3.1. Legacy Component Boundaries

- **Session Responsibility**: `RuntimeExecutionSession` was a purely passive, immutable structural artifact.
- **State Responsibility**: `RuntimeExecutionState` was a structural boundary holding the current `RuntimeExecutionStatus`.
- **Coordinator Responsibility**: `RuntimeExecutionCoordinator` acted as an eligibility and handoff boundary.
- **Executor Responsibility**: `RuntimeExecutor` owned the execution attempt and construction of the `RuntimeExecutionResult`.
- **Identity Continuity**: `RuntimeExecutionIdentity` was the sole identity mechanism.

### 3.2. Legacy Semantic Vocabularies
- **Scheduling vs Execution Distinction**: `SchedulingStatus` answered "What is the scheduling disposition of this work?" (`READY`, `QUEUED`, `DEFERRED`, `BLOCKED`, `REJECTED`).
- **Status vs Outcome Distinction**: `RuntimeExecutionStatus` answered "Where is this execution in its lifecycle?" (`PREPARED`, `READY`, `EXECUTING`, `COMPLETED`, `FAILED`, `ABORTED`). `RuntimeExecutionOutcome` answered "What was the factual terminal outcome?" (`SUCCESS`, `FAILED`, `CANCELLED`).

### 3.3. Lifecycle Conceptual Phases and Transition Matrix
The conceptual lifecycle spanned four phases: Preparation, Eligibility, Execution, and Terminalization.

| Current Status | Target Status | Transition Meaning | Terminal? | Execution Begun? | Result Exists? |
|----------------|---------------|---------------------|-----------|------------------|----------------|
| (None) | `PREPARED` | Structural registration/preparation | No | No | No |
| `PREPARED` | `READY` | Cleared for execution attempt | No | No | No |
| `READY` | `EXECUTING` | Execution attempt begins | No | Yes | No |
| `EXECUTING` | `COMPLETED` | Execution attempt completed normally | Yes | Yes | Yes (`SUCCESS`) |
| `EXECUTING` | `FAILED` | Execution attempt encountered an error | Yes | Yes | Yes (`FAILED`) |
| (Unknown) | `ABORTED` | Structural preparation cleared/aborted | Yes | Varies | No (for structural reset) |

### 3.4. Critical Distinctions and Ambiguities
- **Execution-Attempt Boundary and Rejection Semantics**: No `RuntimeExecutionResult` was constructed for a scheduling rejection (`REJECTED`).
- **ABORTED vs CANCELLED Distinction**: `ABORTED` represented a structural termination/reset of execution preparation. `CANCELLED` represented the outcome of an actual execution attempt.
- **COMPLETED vs SUCCESS Distinction**: `COMPLETED` meant the lifecycle machinery reached a terminal state; `SUCCESS` meant the execution attempt succeeded.
- **FAILED Status vs FAILED Outcome**: `FAILED` status meant abrupt lifecycle termination; `FAILED` outcome meant the execution attempt threw an error.

### 3.5. Lifecycle Invariants
1. `SchedulingStatus` != `RuntimeExecutionStatus`.
2. `RuntimeExecutionStatus` != `RuntimeExecutionOutcome`.
3. `RuntimeExecutionOutcome` contains exactly `SUCCESS`, `FAILED`, and `CANCELLED`.
4. Pre-execution scheduling rejections (`REJECTED`) do not reach the `RuntimeExecutor`.
5. Pre-execution scheduling rejections do not produce a `RuntimeExecutionResult`.
6. Terminal lifecycle states cannot transition back to active lifecycle states.
7. `RuntimeExecutionResult` remains immutable and untouchable after construction.

### 3.6. Transition Validation & Application Contracts
The transition engine (`RuntimeExecutionTransitionEngine`) validated and applied legal transitions (`PREPARED` -> `READY` -> `EXECUTING` -> `COMPLETED`/`FAILED`). It was stateless, did not persist state, and did not execute workloads. The state-bearing component for lifecycle progression was `RuntimeExecutionLifecycleState`, which was fully immutable.

### 3.7. Terminal State & Result Consistency Contract
A lifecycle state and a finalized execution result were not permitted to represent contradictory terminal semantics. 
- `COMPLETED` mapped to `SUCCESS`.
- `FAILED` mapped to `FAILED`.
Consistency checking was strictly observational (via `RuntimeExecutionTerminalConsistencyValidator`).

### 3.8. Lifecycle Failure Semantics Contract
The legacy runtime distinguished between four failure categories: Scheduling rejection, Lifecycle contract violation, Execution failure, and Terminal consistency violation.
- **Lifecycle Contract Violation**: Rejected by the engine, raising a standard `ValueError`. Did not synthesize a result.
- **Execution Failure**: Caught by the `RuntimeExecutor`, producing a `RuntimeExecutionResult` with `FAILED` outcome.
- **Result Creation Boundary**: Actual execution attempts (via `RuntimeExecutor`) were the only authorized source of execution results.
- **Recovery Boundary**: Automatic recovery, retry, restart, resume, rollback, retry queues, and backoff policies were explicitly out of scope.
