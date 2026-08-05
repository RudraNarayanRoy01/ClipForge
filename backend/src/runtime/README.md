# Adaptive AI Runtime

## Why the Runtime Exists
Historically, AI integrations often become tightly coupled to specific providers (e.g., Ollama, Gemini, OpenAI). This creates architectural drift, duplicated logic, and makes future migrations difficult. The Adaptive AI Runtime prevents this by acting as a first-class subsystem that orchestrates AI computation completely independent of providers and hardware.

## Architectural Responsibilities
The Runtime is the **only gateway** to AI computation in the platform. 
It is responsible for:
- Providing abstract contracts for the Application layer to request AI computation.
- Orchestrating capability discovery and execution.
- Managing hardware resources and provider selection dynamically.
- Ensuring dependency inversion (Application -> Runtime -> Providers -> Hardware).

## What Belongs Inside the Runtime
- Capability Registries
- Execution Planners & Schedulers
- Provider Abstractions & Interfaces
- Resource Discovery Mechanisms
- Optimization & Telemetry rules
- Runtime Bootstrap Engine (Lifecycle management and state transitions)

## What Explicitly Does NOT Belong Inside the Runtime
- Domain-specific logic (e.g., Timeline Engine, Campaign Intelligence)
- Hardcoded model names or provider-specific configurations
- Feature-specific AI adapters
- Concrete provider SDKs (those belong in `infrastructure/` or a specialized provider ecosystem)

## Relationship with the Rest of the Platform
- **Application Layer**: Calls the Runtime via abstract interfaces. It does not know *how* or *where* the model runs.
- **Providers/Hardware**: Plug into the Runtime's lower boundary. They know how to execute, but not *why* they are executing.

## Runtime Sprint Evolution (Milestone 6)

The Runtime is designed to evolve progressively without requiring major structural refactoring:

- **Sprint 6.1:** Runtime Foundation (Architecture and boundaries)
- **Sprint 6.2:** Capability Registry
- **Sprint 6.3:** Resource Discovery
- **Sprint 6.4:** Planning Engine
- **Sprint 6.5:** Execution Engine
- **Sprint 6.6:** Provider Ecosystem
- **Sprint 6.7:** Adaptive Optimization
- **Sprint 6.8:** Runtime Certification

## Runtime State Machine

The Runtime operates on a deterministic, immutable state machine initialized by the Bootstrap Engine:
1. `CREATED`
2. `BOOTSTRAPPING`
3. `INITIALIZING`
4. `VALIDATING`
5. `READY` (Healthy operations)
6. `SHUTTING_DOWN`
7. `STOPPED`

A `FAILED` state exists for unrecoverable errors. Illegal transitions are explicitly blocked and enforced via `InvalidRuntimeStateTransitionException`.

## Runtime Component Registry

The Runtime Component Registry is the single source of truth for all Runtime Components. It answers the question: *"What Components exist inside the Runtime?"*

### Runtime Component Model

A `RuntimeComponent` is purely a metadata representation of a component (using immutable frozen dataclasses). It defines fields like ID, name, component type (e.g., `CORE`, `BOOTSTRAP`, `REGISTRY`, `EXECUTION`, etc.), version, capabilities, tags, and dependencies.

### Registry Responsibilities
The Registry is exclusively responsible for:
- Registering Components
- Removing Components
- Querying/Looking up Components by ID or Name
- Enumerating all registered Components
- Exposing immutable point-in-time snapshots
- Exposing component statistics
- Maintaining deterministic registration ordering and preventing duplicates

### Registry Boundaries
The Registry explicitly DOES NOT:
- Instantiate Components
- Resolve dependencies
- Execute Components
- Discover Providers
- Construct Runtime graphs
- Perform scheduling, monitoring, or telemetry operations

It remains completely Provider-agnostic, Hardware-agnostic, and Execution-agnostic.

### Registry Lifecycle

The Registry supports being 'frozen' to prevent subsequent mutations. Components can be registered and removed until the registry is frozen, at which point any modification attempt raises a `RegistryFrozenException`.

## Runtime Dependency Graph

The Runtime Dependency Graph is the canonical structural blueprint of the Runtime. It answers the question: *"How do Runtime Components relate to each other?"*

### Dependency Terminology
- **RuntimeDependency**: An immutable representation of a single directed relationship in the graph.
- **DependencyType**: Pure metadata defining semantics (e.g., `REQUIRED`, `OPTIONAL`, `INITIALIZATION`).
- **DependencyDirection**: Traversal direction (e.g., `FORWARD`, `REVERSE`).
- **DependencySnapshot**: An immutable, deterministic point-in-time capture of the graph.

### Graph Responsibilities
The Dependency Graph is exclusively responsible for:
- Registering and removing dependencies
- Ensuring deterministic topological ordering and traversal
- Performing isolated graph validation (cycle detection, orphan nodes, missing components)
- Yielding immutable snapshots, statistics, and validation results
- Enforcing graph consistency and duplicate protection

### Graph Boundaries
The Dependency Graph explicitly DOES NOT:
- Instantiate Components
- Execute Logic
- Perform Dependency Injection
- Perform Runtime Composition
- Orchestrate Bootstrap or Scheduling
- Contain Hardware or Provider Information

It relies on the `DependencyGraphValidator` to orchestrate validation without holding state, and `DependencyTraversal` to perform pure functional traversal.

## Subsystem Relationships & Ownership Boundaries

Ownership transitions clearly as the Runtime boots:

**Registry** (Controls "What Components exist?")
↓
**Dependency Graph** (Controls "How Components relate?")
↓
**Composition Builder** (Orchestrates composition, validation, and factories)
↓
**Runtime Composition** (Immutable, structural representation of "What Runtime looks like?")
↓
**Future Runtime Executor** (Will control "How they execute" via DI & Instantiation)

Each subsystem strictly obeys the Single Responsibility Principle, ensuring the Runtime remains deterministic and testable at every layer.

## Runtime Composition Foundation

The Runtime Composition Foundation is the canonical assembled Runtime representation. It represents the complete Runtime Foundation assembled from the Runtime Component Registry and Runtime Dependency Graph.

### Purpose
To construct an immutable, structural representation of the Runtime, providing a purely observational snapshot of all components and their relationships without executing or instantiating anything.

### Internal Components & Responsibilities
- **CompositionBuilder**: A thin orchestrator that delegates creation and validation to dedicated components.
- **CompositionValidator**: Exclusively responsible for structural validation (registry presence, graph consistency, boundary enforcement).
- **CompositionStatisticsBuilder**: Computes structural Runtime statistics (component/dependency/root/leaf counts) observationally.
- **CompositionMetadataFactory**: Constructs immutable metadata encapsulating versioning and timestamps.
- **CompositionIdFactory**: Isolates Composition identifier generation for future extensibility.
- **CompositionSnapshotFactory**: Constructs immutable, deterministic point-in-time state snapshots.

### Boundaries & Ownership
The Runtime Composition Foundation explicitly DOES NOT:
- Execute Runtime or Bootstrap
- Instantiate Components or perform Dependency Injection
- Resolve Services or execute Providers
- Execute AI Models or allocate Hardware
- Perform Runtime Monitoring, Scheduling, Telemetry, or Health Analysis

### Deterministic & Immutability Guarantees
- Employs strict immutable data structures (frozen dataclasses, tuples).
- Output is completely determined by the snapshots of the Registry and Dependency Graph.
- Internal snapshots and identifiers are inherently isolated to avoid leakage across sequential builds.
