---
Classification: Foundational Document (Rarely Updated)
Update Frequency: Rarely
Primary Owner: CTO / Principal Architect
---

# Project Constitution

This document is the permanent constitutional foundation for the AI Clipping Platform (ClipForge). It outlines the project vision, long-term objectives, and the architectural philosophy that governs all engineering decisions.

## Project Vision
To build an adaptive, multi-modal AI video editing platform that scales effortlessly to thousands of concurrent users, supporting a diverse and evolving ecosystem of AI providers and hardware configurations without compromising system integrity.

## Long-Term Objectives
1. **Provider Independence**: Seamlessly swap or aggregate capabilities across Ollama, Gemini, OpenAI, etc.
2. **Hardware Adaptability**: Discover and optimize execution across CPU, GPU, and network-attached accelerators dynamically.
3. **Resilient Architecture**: Maintain a core domain that is isolated from rapid changes in the AI tooling landscape.

## Architectural Philosophy
- **Elegance over Cleverness**: Code should be readable and its intent obvious.
- **Modularity over Convenience**: Strong boundaries prevent architectural rot.
- **Composition over Inheritance**: Favor combining small, focused components.
- **Interfaces over Implementations**: Depend on contracts, not concrete classes.

## Clean & Hexagonal Architecture Principles
We employ Clean Architecture and Hexagonal Architecture (Ports and Adapters) principles:
- **Core Domain**: The center of the application, containing business rules and domain entities. It has NO outbound dependencies.
- **Application Layer**: Use cases that orchestrate domain logic. Depends on Core Domain.
- **Adapters**: Connect the Application Layer to external concerns (Database, UI, AI Providers). Depends on Application Layer interfaces.
- **Dependency Inversion**: All dependencies point inward toward the core domain.

## Architectural Invariants
These rules must **never** be violated:
1. **Application Layer must never know AI providers.**
2. **Application Layer must never know hardware.**
3. **Application Layer must never bypass the Runtime.**
4. **Runtime must remain provider agnostic.**
5. **Runtime must remain hardware agnostic.**
6. **Infrastructure must never leak into Application or Domain layers.**
7. **Dependency inversion must always be preserved.**
8. **Clean Architecture and Hexagonal Architecture remain non-negotiable.**
9. **Interfaces should be introduced only when they provide genuine architectural value.**
10. **Temporary shortcuts should never become permanent architecture.**

## Engineering & Development Philosophy
- **Architecture First**: We never optimize for generating the most code. We optimize for building the best software architecture.
- **Testability & Monitorability**: Every subsystem must be designed to be thoroughly tested and monitored via OpenTelemetry.
- **Long-term Roadmap**: We prioritize building foundations that can support future features (e.g., plugins, parallel processing) over immediate minimum viable products if the MVP introduces architectural debt.
