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
