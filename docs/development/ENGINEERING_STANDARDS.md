---
Classification: Living Document (Continuously Updated)
Update Frequency: Continuously
Primary Owner: CTO / Principal Architect
---

# Engineering Standards

This document enforces the technical standards and architectural constraints for ClipForge.

## Naming Conventions
- Interfaces: Prefixed with `I` (e.g., `IAIProvider`).
- Directories: snake_case for Python modules.
- Abstract base classes should clearly communicate their role (e.g., `AbstractScheduler`).

## Module & Package Guidelines
- Empty modules should not be created blindly. If an empty module exists, it must be documented as exactly one of: **Reserved, Planned, Deprecated, Obsolete**.
- Package dependencies should flow inwards. An inner module should never import an outer module.

## Dependency Rules
- **Domain**: Depends on nothing.
- **Application**: Depends on Domain.
- **Adapters / Runtime**: Depends on Application Contracts.
- **Infrastructure**: Depends on Adapters / Runtime Contracts.

## Architectural Smells
These are non-negotiable rules. If these smells are detected, the code must be refactored:

**Never:**
- Skip abstractions because "only one implementation exists today".
- Couple the Application Layer directly to Infrastructure (e.g., calling `ffmpeg` from a Use Case directly).
- Introduce bidirectional dependencies between modules.
- Hardcode provider selection (e.g., `if model == "gemini"` in the domain).
- Add Runtime logic specific to one distinct feature.
- Break dependency inversion.
