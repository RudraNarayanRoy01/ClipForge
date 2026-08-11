# Runtime Execution Lifecycle Contract

## 1. Purpose

The purpose of this contract is to establish the canonical architectural boundaries, states, outcomes, and transitions of the Runtime Execution Lifecycle. This document formally dictates "what the lifecycle means" structurally, entirely separate from the execution machinery that performs the work. 

## 2. Component Boundaries and Ownership Matrix

The execution lifecycle explicitly isolates scheduling, preparation, execution, and terminalization into distinct concepts owned by distinct components.

| Concern | Owner |
|---------|-------|
| Scheduling disposition | Scheduling layer |
| Execution eligibility | `RuntimeExecutionCoordinator` |
| Execution identity | `RuntimeExecutionIdentity` |
| Execution context | `RuntimeExecutionSession` |
| Lifecycle position | `RuntimeExecutionLifecycleState` |
| Lifecycle transition semantics | Lifecycle contract (this document) |
| Execution attempt | `RuntimeExecutor` |
| Terminal execution record | `RuntimeExecutionResult` |
| Terminal outcome taxonomy | `RuntimeExecutionOutcome` |

### 2.1. Session Responsibility
`RuntimeExecutionSession` is a purely passive, immutable structural artifact. It represents the execution context and bounds the execution, but it does **not** orchestrate transitions, invoke providers, schedule work, or construct execution results.

### 2.2. State Responsibility
`RuntimeExecutionState` is a structural boundary that encapsulates `RuntimeExecutionStateIdentity`. The active position of an execution in the lifecycle is owned specifically by `RuntimeExecutionLifecycleState`, an immutable representation holding the current `RuntimeExecutionStatus`.

### 2.3. Coordinator Responsibility
`RuntimeExecutionCoordinator` is strictly an eligibility and handoff boundary. It evaluates `SchedulingDecision.status == SchedulingStatus.READY`. If eligible, it invokes the `RuntimeExecutor` and propagates the returned result. It does **not** perform execution itself, manage state transitions, or classify failures.

### 2.4. Executor Responsibility
`RuntimeExecutor` owns the actual execution attempt, the execution timing, the exception boundary, and the construction of the terminal `RuntimeExecutionResult`. It owns the mapping to `RuntimeExecutionOutcome` based on the success or failure of the execution attempt.

### 2.5. Result Responsibility
`RuntimeExecutionResult` is an immutable, historical, terminal record of an actual execution attempt. It cannot exist if execution was not attempted (e.g., due to scheduling rejection).

### 2.6. Identity Continuity
`RuntimeExecutionIdentity` remains the sole, canonical identity mechanism throughout the lifecycle. No secondary identifiers (e.g., lifecycle ID, result ID, or scheduling replacement ID) are permitted to override or duplicate it.

## 3. Semantic Vocabularies

The contract enforces strict separation between Scheduling, Lifecycle Status, and Terminal Outcome.

### 3.1. Scheduling vs Execution Distinction
`SchedulingStatus` answers: *"What is the scheduling disposition of this work?"*
It represents scheduling decisions **before** execution.

Vocabulary:
- `READY`
- `QUEUED`
- `DEFERRED`
- `BLOCKED`
- `REJECTED`

### 3.2. Status vs Outcome Distinction
`RuntimeExecutionStatus` answers: *"Where is this execution in its lifecycle?"*
It represents the ongoing lifecycle position of the execution structurally.

Vocabulary:
- `PREPARED`
- `READY`
- `EXECUTING`
- `COMPLETED`
- `FAILED`
- `ABORTED`

`RuntimeExecutionOutcome` answers: *"What was the factual terminal outcome of an execution attempt?"*
It represents the historical, terminal fact evaluated by the executor.

Vocabulary:
- `SUCCESS`
- `FAILED`
- `CANCELLED`

**Crucial Distinction**: `RuntimeExecutionStatus` describes the state of the lifecycle machinery, while `RuntimeExecutionOutcome` describes the result of the domain work attempted.

## 4. Lifecycle Conceptual Phases and Transition Matrix

The conceptual lifecycle spans four phases:
1. **Preparation**: Organizing metadata and context (`PREPARED`, `READY`). Execution has not begun. No result exists.
2. **Eligibility**: `RuntimeExecutionCoordinator` evaluates the `SchedulingDecision`.
3. **Execution**: The attempt begins in `RuntimeExecutor` (`EXECUTING`).
4. **Terminalization**: The attempt concludes (`COMPLETED`, `FAILED`, `ABORTED`).

### 4.1. Transition Matrix
**Note on Machinery**: This transition matrix describes *architectural semantics* and is an abstract representation of the documented conceptual lifecycle. It is **not** an executable state-transition engine. The runtime currently does not enforce active transition logic within these states.

Based on the existing repository contract, the following transitions represent conceptual progression:

| Current Status | Target Status | Transition Meaning | Terminal? | Execution Begun? | Result Exists? |
|----------------|---------------|---------------------|-----------|------------------|----------------|
| (None) | `PREPARED` | Structural registration/preparation | No | No | No |
| `PREPARED` | `READY` | Cleared for execution attempt | No | No | No |
| `READY` | `EXECUTING` | Execution attempt begins | No | Yes | No |
| `EXECUTING` | `COMPLETED` | Execution attempt completed normally | Yes | Yes | Yes (`SUCCESS`) |
| `EXECUTING` | `FAILED` | Execution attempt encountered an error | Yes | Yes | Yes (`FAILED`) |
| (Unknown) | `ABORTED` | Structural preparation cleared/aborted | Yes | Varies | No (for structural reset) |

*Note on ABORTED*: The exact legal source states for transitioning to `ABORTED` cannot be conclusively established from the current implementation machinery because `ABORTED` is enacted through a structural reset via `RuntimeExecutionManager.clear_execution()`. It acts as a termination of the lifecycle preparation rather than a targeted state transition.

*Forbidden Transitions*:
- Terminal states (`COMPLETED`, `FAILED`, `ABORTED`) **cannot** regress to active states (`PREPARED`, `READY`, `EXECUTING`) unless a new identity/attempt is structurally established (Retry is currently out of scope).

### 4.2. Terminal State Semantics
A terminal lifecycle state means normal lifecycle progression has ended. No further transitions are possible. Current terminal states are `COMPLETED`, `FAILED`, and `ABORTED`. 

## 5. Critical Distinctions and Ambiguities

### 5.1. Execution-Attempt Boundary and Rejection Semantics
A `SchedulingStatus.REJECTED` (or `QUEUED`, `DEFERRED`, `BLOCKED`) means the work was deemed ineligible *before* execution.
**Contract Rule**: No execution attempt occurs for non-READY decisions. Therefore, **no `RuntimeExecutionResult` may be constructed for a scheduling rejection**. `REJECTED` is strictly a scheduling concept and does not exist in `RuntimeExecutionOutcome`.

### 5.2. ABORTED vs CANCELLED Distinction
- `RuntimeExecutionStatus.ABORTED` represents an existing structural termination/reset of execution *preparation* as evidenced by `RuntimeExecutionManager.clear_execution()`. It is currently a lifecycle/preparation termination concept.
- `RuntimeExecutionOutcome.CANCELLED` represents the terminal factual outcome of an *actual execution attempt* that was interrupted or cancelled.
**Contract Rule**: `ABORTED` and `CANCELLED` represent distinct concepts. `ABORTED` != `CANCELLED`. `ABORTED` does not automatically imply an execution attempt occurred, nor does it imply a `RuntimeExecutionResult` exists. There is **NO AUTOMATIC EQUIVALENCE** or mapping between them in this contract.

### 5.3. COMPLETED vs SUCCESS Distinction
- `RuntimeExecutionStatus.COMPLETED` indicates that the lifecycle machinery reached its completed terminal state.
- `RuntimeExecutionOutcome.SUCCESS` indicates that the execution attempt itself succeeded.
**Contract Rule**: `COMPLETED` and `SUCCESS` are distinct semantic dimensions. They are related but are not enum aliases or intrinsically identical concepts. A successfully completed execution attempt may result in `RuntimeExecutionStatus.COMPLETED` + `RuntimeExecutionOutcome.SUCCESS`, but the two values belong to different semantic dimensions. There is no mandatory `COMPLETED == SUCCESS` mapping.

### 5.4. FAILED Status vs FAILED Outcome
Likewise, `RuntimeExecutionStatus.FAILED` represents a lifecycle that terminated abruptly, whereas `RuntimeExecutionOutcome.FAILED` represents the factual outcome that the execution attempt threw an error. 

## 6. Lifecycle Invariants
1. `SchedulingStatus` != `RuntimeExecutionStatus`.
2. `RuntimeExecutionStatus` != `RuntimeExecutionOutcome`.
3. `RuntimeExecutionOutcome` contains exactly `SUCCESS`, `FAILED`, and `CANCELLED`.
4. Pre-execution scheduling rejections (`REJECTED`) do not reach the `RuntimeExecutor`.
5. Pre-execution scheduling rejections do not produce a `RuntimeExecutionResult`.
6. Terminal lifecycle states cannot transition back to active lifecycle states.
7. `RuntimeExecutionResult` remains immutable and untouchable after construction.

## 7. Future / Out-of-Scope Functionality
- **Retry Semantics**: Automatic recovery and retry semantics are explicitly outside the scope of Sprint 6A.8.1.
- **Cancellation Machinery**: The mechanisms for cancelling an execution attempt (cancellation tokens, queues, thread aborts) are not implemented. Only the semantic outcome (`CANCELLED`) is defined.
- **State Machine Implementation**: The active transition engine and orchestrator for moving between these states is deferred to subsequent batches.

## 8. Transition Validation Contract

### Valid transitions
- `PREPARED` → `READY`
- `READY` → `EXECUTING`
- `EXECUTING` → `COMPLETED`
- `EXECUTING` → `FAILED`

### Invalid transitions
All other transitions are invalid under the current contract. This includes skipped transitions, backward regressions, and all self-transitions (e.g., `READY` → `READY`).

### Terminal states
- `COMPLETED`
- `FAILED`
- `ABORTED`

### ABORTED
> `ABORTED` is a structural/preparation reset status and is distinct from `CANCELLED`. The current architecture does not establish formal incoming lifecycle transitions into `ABORTED`; therefore 6A.8.2 does not certify any such transition.

### Validation vs mutation
> The transition validator answers whether a transition is valid. It does not perform, persist, or mutate the transition.

### Initialization
> Initialization to `PREPARED` is not represented as a transition by the validator.

## 9. Transition Application Contract

### Validation vs Application
> **TransitionValidator**: Determines whether a transition is legal.
> **TransitionEngine**: Applies a legal transition and returns the target status.

The Transition Engine does not own lifecycle state. It produces the resulting `RuntimeExecutionStatus` for a requested transition and does not mutate `RuntimeExecutionState`.

### Engine Constraints
The Transition Engine:
- is stateless;
- does not own lifecycle state;
- does not persist state;
- does not execute workloads;
- does not orchestrate;
- does not schedule;
- does not manage providers;
- does not implement cancellation;
- does not implement retry;
- does not duplicate the transition matrix.

### Immutable Semantics
Explicitly preserved:
- `ABORTED` != `CANCELLED`
- `COMPLETED` != `SUCCESS`

## 10. State Application Contract

### 10.1 Dedicated Component Justification
The state-bearing component for lifecycle progression is `RuntimeExecutionLifecycleState`. It isolates the "what state am I in?" concern from the structural identity domains covered by `RuntimeExecutionState` and `RuntimeExecutionSession`. These latter structures are purely passive composite boundaries, whereas `RuntimeExecutionLifecycleState` exclusively captures the real-time position within the `RuntimeExecutionStatus` taxonomy.

### 10.2 Immutability and State Replacement
`RuntimeExecutionLifecycleState` is fully immutable. A state progression does not mutate the current state object in place. Instead, a legal transition triggers the creation of a *new* state instance encapsulating the transitioned `RuntimeExecutionStatus`.

### 10.3 State Identity vs Dependency Identity
A lifecycle state's semantic identity is defined exclusively by its `RuntimeExecutionStatus`. The component leverages `RuntimeExecutionTransitionEngine` purely as an injected implementation dependency. This engine's own object identity never bleeds into the conceptual equality or semantic definition of the lifecycle state.

### 10.4 Initial State and Delegation
The state boundary defaults intrinsically to `PREPARED`. From there, it delegates 100% of state transition application to the `RuntimeExecutionTransitionEngine`. It holds zero standalone validation logic and never mirrors or overrides the transition matrix managed by the validator.

### 10.5 Strict Execution and Scheduling Disconnect
The component has no awareness or dependency regarding execution outcomes (`RuntimeExecutionOutcome`) or scheduling decisions (`SchedulingStatus`). Its API strictly expects `RuntimeExecutionStatus`, reflecting its dedicated role in managing abstract lifecycle bounds.

### 10.6 Non-Responsibilities
The `RuntimeExecutionLifecycleState` boundary explicitly:
- Does **not** constitute a fully-fledged executable workflow state machine.
- Does **not** include or invoke any persistence/event sourcing logic.
- Does **not** orchestrate scheduling or manage task queues.
- Does **not** handle or cache a state transition history.
