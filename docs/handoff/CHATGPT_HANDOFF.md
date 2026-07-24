---
Classification: Living Document (Continuously Updated)
Update Frequency: Continuously
Primary Owner: CTO / Principal Architect
---

# ChatGPT Handoff

This document is the permanent bootstrap guide for future AI (ChatGPT/Gemini) sessions working on the ClipForge repository.

**BEFORE PROCEEDING**, any new AI agent must read this document to understand the current state of the platform.

## Current Context
- **Current Milestone**: Milestone 6 (Adaptive AI Runtime)
- **Current Sprint**: Sprint 6.1
- **Current Batch**: Batch 6.1.1 (Runtime Foundation)

## Active Architecture
The platform is built on Hexagonal Architecture. The core application logic must NEVER depend on AI providers, hardware configurations, or database implementations.
The new `Adaptive AI Runtime` subsystem acts as the orchestrator for all AI processing.

## Active Roadmap
We are building out the AI Runtime systematically across Sprint 6.x. The current focus is purely architectural; no execution logic should exist yet.

## Important Constraints
1. Do not introduce provider-specific logic to the Application layer.
2. Adhere to the estimated change budget for each Batch.
3. Preserve dependency direction at all costs.

## Engineering Workflow
ClipForge uses AI-assisted engineering. We plan before we code. You must:
1. Produce an implementation plan.
2. Request explicit user feedback.
3. Document architectural changes in `ARCHITECTURE_STATE.md` and `COMPONENT_CATALOG.md`.
4. Validate changes against our `PROJECT_CONSTITUTION.md`.

## Primary Architecture Documents to Read First
- `docs/architecture/PROJECT_CONSTITUTION.md`
- `docs/architecture/ARCHITECTURE_STATE.md`
- `docs/architecture/ARCHITECTURE_MAP.md`
- `docs/development/ENGINEERING_STANDARDS.md`
