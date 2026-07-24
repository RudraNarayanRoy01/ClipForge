# Runtime Core

## Purpose

The `core` package defines the fundamental internal architectural framework of the Adaptive AI Runtime. 

It exists to establish the Runtime's lifecycle, bootstrap mechanism, and extension philosophy. It provides the central nervous system that future Runtime capabilities will plug into.

## Responsibilities

- **Lifecycle Coordination**: Defining the states the Runtime goes through (Uninitialized → Bootstrapping → Initialized → Shutting Down → Shutdown) and notifying components of transitions.
- **Bootstrap Architecture**: Establishing the entry point for the Runtime and defining startup responsibilities.
- **Extension Points**: Owning the extension points that allow the Runtime to grow according to the Open/Closed Principle.

## What Belongs Here

- Lifecycle state machine and coordinator.
- The Runtime Bootstrap class.
- Interfaces for Extension Points and Extensions.

## What Explicitly Does NOT Belong Here

- Extension registrations (these belong in specific registries).
- Provider logic or hardware discovery.
- AI execution, model loading, or prompt management.
- Concrete extensions (e.g., Capability Registry belongs in its own package).

## Expected Future Growth

The `core` package is designed to be highly stable. Most future growth in the Runtime will occur in sibling packages (e.g., `registry`, `planner`, `scheduler`, `providers`) which will implement the `IRuntimeExtension` interface defined here and plug into the `IRuntimeExtensionPoint`s established by the bootstrap process.
