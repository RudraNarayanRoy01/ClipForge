---
Classification: Foundational Document (Rarely Updated)
Update Frequency: Rarely
Primary Owner: CTO / Principal Architect
---

# ADR 001: Clean & Hexagonal Architecture

**Date**: 2026-07-24 (Formalized)
**Status**: Accepted

## Context
ClipForge operates in a rapidly evolving ecosystem. AI providers, hardware availability, and UI frameworks change frequently. If our core business rules are coupled to these external volatile components, the platform will become impossible to maintain or migrate.

## Decision
We mandate the strict use of Clean Architecture and Hexagonal Architecture principles across the entire platform.
- The Core Domain contains business rules and has NO external dependencies.
- The Application Layer orchestrates the domain via Interfaces (Ports).
- Adapters (Infrastructure, Database, API, AI Runtime) implement these interfaces.
- All dependency arrows must point inwards toward the Domain.

## Consequences
- **Positive**: The platform can easily swap a database, UI, or AI provider without rewriting domain logic.
- **Positive**: High testability via mocked interfaces.
- **Negative**: Increased initial complexity. Requires defining interfaces and mapping DTOs between layers.

## Compliance
This decision is foundational. Any code that violates dependency inversion will fail Architecture Review.
