# Architecture Overview

This document serves as the high-level index for the AI Clipping Platform (ClipForge) architectural specifications.

## Documentation Index

Detailed architectural decisions, blueprints, and records are maintained in the following locations:

- **[Project Constitution](docs/architecture/PROJECT_CONSTITUTION.md)**: The permanent constitutional foundation, vision, and architectural invariants.
- **[Architecture State](docs/architecture/ARCHITECTURE_STATE.md)**: Living snapshot of the platform's current architectural state.
- **[Architecture Map](docs/architecture/ARCHITECTURE_MAP.md)**: High-level navigation map of the platform's topology.
- **[Component Catalog](docs/architecture/COMPONENT_CATALOG.md)**: Inventory of subsystems, responsibilities, and implementation states.
- **[Architecture Certification](docs/certification/ARCHITECTURE_CERTIFICATION.md)**: Sprint-level architectural readiness and health certifications.
- **[Database Migrations](backend/docs/DATABASE_MIGRATIONS.md)**: Alembic configuration, schema versioning, and migration policies.
- **[Planning Pipeline](backend/docs/planning_pipeline.md)**: Specifications for the multimodal AI processing pipeline.
- **[Architecture Walkthrough](backend/docs/architecture_walkthrough.md)**: High-level walkthrough of the system layers and boundaries.

## Assumptions

The architecture relies on the following documented assumptions:

1. **Supported Platforms**: Windows is the primary developer platform. Testing environments assume modern Unix-like or Windows environments capable of running Python 3.9+ and Node 18+.
2. **External Dependencies**:
   - `ffmpeg` must be globally available in the system PATH for the `FfmpegVideoProcessor` to function correctly.
3. **AI Providers**:
   - `Ollama` is expected to be running locally (or available via network) for LLM reasoning capabilities.
   - `faster-whisper` is expected to have sufficient memory (CPU/GPU) to run locally within the application process.
4. **Toolchain Versions**:
   - Python `>=3.9` is required.
   - Node.js `>=18.0` is required.
   - Package lockfiles (`requirements.txt`, `package-lock.json`) are strictly adhered to for reproducible environments.
